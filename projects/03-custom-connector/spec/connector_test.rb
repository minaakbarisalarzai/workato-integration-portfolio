# frozen_string_literal: true
# Deterministic, offline behavior tests. These emulate the small subset of
# Workato's DSL used by this connector; run an SDK test separately in Workato.
require 'minitest/autorun'
require 'json'

CONNECTOR = eval(File.read(File.expand_path('../connector.rb', __dir__)), TOPLEVEL_BINDING, 'connector.rb')

class FakeRequest
  attr_reader :path, :query
  def initialize(path, status:, body:, headers:)
    @path, @status, @body, @headers = path, status, body, headers
  end
  def params(query)
    @query = query
    self
  end
  def after_error_response(_pattern, &block)
    block.call(@status, @body, @headers, 'HTTP error') if @status >= 400
    self
  end
  def after_response(&block)
    block.call(@status, @body, @headers)
  end
  def map(&block)
    @body.map(&block)
  end
end

class FakeRuntime
  attr_reader :request, :requests
  def initialize(connector, response = {}, page_responses: nil, **response_keywords)
    @connector = connector
    @response = { status: 200, body: [], headers: {} }.merge(response).merge(response_keywords)
    @page_responses = page_responses
    @requests = []
  end
  def call(method_name, *args)
    instance_exec(*args, &@connector[:methods].fetch(method_name.to_sym))
  end
  def error(message)
    raise ArgumentError, message
  end
  def get(path)
    response = @page_responses ? @page_responses.fetch(@requests.size, @response) : @response
    @request = FakeRequest.new(path, **response)
    @requests << @request
    @request
  end
  def run_action(input)
    instance_exec({}, input, &@connector[:actions][:list_repository_issues][:execute])
  end
  def run_picklist(name, **params)
    instance_exec({}, **params, &@connector[:pick_lists].fetch(name))
  end
end

class ConnectorTest < Minitest::Test
  def setup
    @sample = JSON.parse(File.read(File.expand_path('../fixtures/issues_page.json', __dir__)))
  end

  def test_exactly_one_action_and_read_only
    assert_equal [:list_repository_issues], CONNECTOR[:actions].keys
    assert_includes CONNECTOR[:actions][:list_repository_issues][:retry_on_request], 'GET'
  end

  def test_normalizes_issues_and_excludes_pull_requests
    runtime = FakeRuntime.new(CONNECTOR, body: @sample,
      headers: { 'link' => '<https://api.github.com/repos/demo/issues?page=2>; rel="next"' })
    result = runtime.run_action('owner' => 'octocat', 'repo' => 'Hello-World', 'per_page' => 2)
    assert_equal '/repos/octocat/Hello-World/issues', runtime.request.path
    assert_equal 2, runtime.request.query[:per_page]
    assert_equal 1, result['count']
    assert_equal 'Demo bug', result['issues'][0]['title']
    assert_equal 'octocat', result['issues'][0]['author_login']
    assert_equal [{ 'name' => 'bug' }], result['issues'][0]['labels']
    assert_equal 2, result['next_page']
    assert_equal true, result['has_more']
  end

  def test_last_page_has_no_next_page
    runtime = FakeRuntime.new(CONNECTOR, body: @sample, headers: {})
    result = runtime.run_action('owner' => 'octocat', 'repo' => 'Hello-World')
    assert_nil result['next_page']
    assert_equal false, result['has_more']
  end

  def test_rejects_missing_owner
    assert_raises(ArgumentError) do
      FakeRuntime.new(CONNECTOR).run_action('owner' => '', 'repo' => 'demo')
    end
  end

  def test_rejects_untrusted_path_characters
    err = assert_raises(ArgumentError) do
      FakeRuntime.new(CONNECTOR).run_action('owner' => '../admin', 'repo' => 'demo')
    end
    assert_match(/only letters/, err.message)
  end

  def test_rejects_invalid_page_size
    err = assert_raises(ArgumentError) do
      FakeRuntime.new(CONNECTOR).run_action('owner' => 'octocat', 'repo' => 'demo', 'per_page' => 101)
    end
    assert_match(/between 1 and 100/, err.message)
  end

  def test_rejects_invalid_filter
    err = assert_raises(ArgumentError) do
      FakeRuntime.new(CONNECTOR).run_action('owner' => 'octocat', 'repo' => 'demo', 'state' => 'unexpected')
    end
    assert_match(/Invalid issue state/, err.message)
  end

  def test_rate_limit_message_is_actionable
    runtime = FakeRuntime.new(CONNECTOR, status: 403, body: { 'message' => 'Forbidden' },
      headers: { 'x-ratelimit-remaining' => '0' })
    error = assert_raises(ArgumentError) do
      runtime.run_action('owner' => 'octocat', 'repo' => 'demo')
    end
    assert_match(/rate limit/, error.message)
  end

  def test_404_error_is_actionable
    runtime = FakeRuntime.new(CONNECTOR, status: 404, body: { 'message' => 'Not Found' })
    error = assert_raises(ArgumentError) do
      runtime.run_action('owner' => 'octocat', 'repo' => 'demo')
    end
    assert_match(/token visibility/, error.message)
  end

  def test_dynamic_repository_picklist
    runtime = FakeRuntime.new(CONNECTOR, body: [{ 'name' => 'demo', 'owner' => { 'login' => 'octocat' } }, { 'name' => 'test', 'owner' => { 'login' => 'octocat' } }])
    assert_equal [['demo', 'demo'], ['test', 'test']], runtime.run_picklist(:owner_repositories, owner: 'octocat')
  end

  def test_dependent_label_picklist
    runtime = FakeRuntime.new(CONNECTOR, body: [{ 'name' => 'bug' }])
    assert_equal [['bug', 'bug']], runtime.run_picklist(:repository_labels, owner: 'octocat', repo: 'demo')
  end
  def test_auth_repository_picker_filters_owner_and_reads_private_repo
    runtime = FakeRuntime.new(CONNECTOR, body: [
      { 'name' => 'private-demo', 'private' => true, 'owner' => { 'login' => 'octocat' } },
      { 'name' => 'different-owner', 'owner' => { 'login' => 'another' } }
    ])
    assert_equal [['private-demo', 'private-demo']], runtime.run_picklist(:owner_repositories, owner: 'octocat')
    assert_equal '/user/repos', runtime.request.path
  end

  def test_repository_picker_fetches_two_pages
    responses = [
      { status: 200, body: [{ 'name' => 'a', 'owner' => { 'login' => 'octocat' } }],
        headers: { 'link' => '<https://api.github.com/user/repos?page=2>; rel="next"' } },
      { status: 200, body: [{ 'name' => 'b', 'owner' => { 'login' => 'octocat' } }], headers: {} }
    ]
    runtime = FakeRuntime.new(CONNECTOR, page_responses: responses)
    assert_equal [['a', 'a'], ['b', 'b']], runtime.run_picklist(:owner_repositories, owner: 'octocat')
    assert_equal [1, 2], runtime.requests.map { |r| r.query[:page] }
  end

  def test_label_picker_fetches_two_pages
    responses = [
      { status: 200, body: [{ 'name' => 'bug' }],
        headers: { 'Link' => '<https://api.github.com/repos/a/b/labels?page=2>; rel="next"' } },
      { status: 200, body: [{ 'name' => 'help wanted' }], headers: {} }
    ]
    runtime = FakeRuntime.new(CONNECTOR, page_responses: responses)
    assert_equal [['bug', 'bug'], ['help wanted', 'help wanted']],
      runtime.run_picklist(:repository_labels, owner: 'octocat', repo: 'demo')
  end

  def test_invalid_non_integer_inputs_rejected_before_api
    ['10junk', '2.5', -1, 0, 101].each do |bad|
      runtime = FakeRuntime.new(CONNECTOR)
      assert_raises(ArgumentError) do
        runtime.run_action('owner' => 'octocat', 'repo' => 'demo', 'per_page' => bad)
      end
      assert_equal 0, runtime.requests.length
    end
  end

  def test_422_error_includes_remote_message
    runtime = FakeRuntime.new(CONNECTOR, status: 422,
      body: { 'message' => 'Page number is invalid' })
    raised = assert_raises(ArgumentError) do
      runtime.run_action('owner' => 'octocat', 'repo' => 'demo')
    end
    assert_match(/Page number is invalid/, raised.message)
  end

  def test_remote_message_redacts_token
    runtime = FakeRuntime.new(CONNECTOR, status: 422,
      body: { 'message' => 'bad github_pat_SECRET1234 value' })
    raised = assert_raises(ArgumentError) do
      runtime.run_action('owner' => 'octocat', 'repo' => 'demo')
    end
    refute_includes raised.message, 'SECRET1234'
    assert_includes raised.message, '[REDACTED]'
  end

  def test_issue_count_excludes_pr_but_has_more_uses_api_links
    runtime = FakeRuntime.new(CONNECTOR, body: @sample,
      headers: { 'link' => '<https://api.github.com/repos/demo/issues?page=2>; rel="next"' })
    result = runtime.run_action('owner' => 'octocat', 'repo' => 'demo', 'per_page' => 2)
    assert_equal 1, result['count']
    assert_equal true, result['has_more']
  end

  def test_rate_limit_secondary_message
    runtime = FakeRuntime.new(CONNECTOR, status: 403,
      body: { 'message' => 'You have exceeded a secondary rate limit' },
      headers: { 'x-ratelimit-remaining' => '100' })
    raised = assert_raises(ArgumentError) do
      runtime.run_action('owner' => 'octocat', 'repo' => 'demo')
    end
    assert_match(/rate limit/, raised.message)
  end

end
