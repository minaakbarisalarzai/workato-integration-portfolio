
 =============================================================================
# GitHub Issue Explorer — Workato Custom Connector
# =============================================================================
#
# Author:          Mina Akbari
# Project:         Workato Integration Engineering Portfolio
# Version:         2.0.0
# Created:         November 2026
# Last Revised:    November 3, 2026
# Language:        Ruby
# Framework:       Workato Connector SDK
# Integration:     GitHub REST API
#
# DESCRIPTION
# -----------
# A custom Workato connector designed to retrieve, filter, and explore
# GitHub repository issues through a secure, configurable REST integration.
#
# The connector demonstrates production-oriented integration patterns,
# including:
#
#   - API token authentication and connection validation
#   - Reusable helper methods and modular connector design
#   - Dynamic and dependent repository/label picklists
#   - Input validation with descriptive error messages
#   - GitHub API response handling and normalized output schemas
#   - Pagination and response metadata
#   - HTTP error handling and bounded retry configuration
#   - Automated unit tests and integration testing
#
# DESIGN PRINCIPLES
# -----------------
# Security, maintainability, clear error reporting, reusable logic,
# and predictable API behavior.
#
# SECURITY
# --------
# This connector is independently developed for demonstration purposes.
# It uses the GitHub public API and contains no proprietary employer
# code, customer data, or embedded authentication credentials.
#
# =============================================================================

{
  title: 'GitHub Issue Explorer',
  subtitle: 'Read-only GitHub issue discovery with safe pagination and actionable errors',
  description: 'Explore repository issues using a fine-grained personal access token.',

  connection: {
    fields: [
      {
        name: 'personal_access_token',
        label: 'Fine-grained GitHub personal access token',
        control_type: 'password',
        optional: false,
        hint: 'Use a fine-grained token with repository Issues: Read. ' \
              'Restrict access to only the demonstration repository.'
      }
    ],
    authorization: {
      type: 'api_key',
      apply: lambda do |connection|
        headers(
          'Authorization' => "Bearer #{connection['personal_access_token']}",
          'Accept' => 'application/vnd.github+json',
          'X-GitHub-Api-Version' => '2026-03-10',
          'User-Agent' => 'workato-issue-explorer-demo'
        )
      end
    },
    base_uri: lambda do |_connection|
      'https://api.github.com'
    end
  },

  test: lambda do |_connection|
    get('/user').after_error_response(/.*/) do |code, _body, _headers, _message|
      error("GitHub authentication failed (HTTP #{code}). Check your token and its expiration.")
    end
  end,

  methods: {
    # Keep API access fixed to api.github.com. Never accept user-supplied URLs.
    validate_slug: lambda do |value, label|
      candidate = value.to_s.strip
      error("#{label} is required") if candidate.empty?
      unless candidate.match?(/\A[A-Za-z0-9_.-]+\z/) && candidate != '.' && candidate != '..'
        error("#{label} must contain only letters, numbers, dots, hyphens, or underscores")
      end
      candidate
    end,
    # Numeric inputs should not silently truncate values such as '2.5' or '10abc'.
    positive_integer: lambda do |value, default_value, upper_bound, label|
      candidate = value.nil? || value == '' ? default_value.to_s : value.to_s
      error("#{label} must be a whole number between 1 and #{upper_bound}") unless candidate.match?(/\A[0-9]+\z/)
      parsed = candidate.to_i
      error("#{label} must be a whole number between 1 and #{upper_bound}") unless parsed.between?(1, upper_bound)
      parsed
    end,
    github_error: lambda do |code, body, headers|
      message = body.is_a?(Hash) ? body['message'].to_s : ''
      # Never expose credentials or the full remote error body in recipe logs.
      message = message.gsub(/(?:ghp_|ghu_|ghs_|ghr_|github_pat_)[A-Za-z0-9_]+/, '[REDACTED]')
                       .gsub(/[\r\n]+/, ' ')[0, 180]
      case code.to_i
      when 401
        'GitHub rejected the access token (401). Reconnect with a valid token.'
      when 403, 429
        remaining = headers.is_a?(Hash) ? (headers['x-ratelimit-remaining'] || headers['X-RateLimit-Remaining']) : nil
        if remaining.to_s == '0' || code.to_i == 429 || message.downcase.include?('rate limit')
          'GitHub API rate limit reached (403/429). Review the rate-limit reset and retry later.'
        else
          'GitHub denied access (403). Check selected repositories and Issues: Read permissions.'
        end
      when 404
        'Repository or issues endpoint not found (404). Check owner/repository and token visibility.'
      when 422
        "GitHub rejected the request (422). Check the filters and page number.#{message.empty? ? '' : " GitHub says: #{message}"}"
      when 500..599
        "GitHub server error (#{code}). Try again later."
      else
        "GitHub API request failed (HTTP #{code})#{message.empty? ? '' : ": #{message}"}"
      end
    end,
    # Fetch bounded pages for SDK dropdowns. The last page may be shorter
    # than 100 items; a Link rel=next is the authoritative pagination signal.
    # A safety bound keeps the editor responsive for accounts with huge lists.
    fetch_picklist_pages: lambda do |path, query, max_pages|
      entries = []
      current_page = 1
      while current_page <= max_pages
        response = get(path)
          .params(query.merge(page: current_page, per_page: 100))
          .after_error_response(/.*/) do |code, body, headers, _message|
            error(call('github_error', code, body, headers))
          end
          .after_response do |_code, body, headers|
            error('Unexpected GitHub list response') unless body.is_a?(Array)
            { 'items' => body, 'next_page' => call('next_page_from_link', headers) }
          end
        entries.concat(response['items'])
        next_page = response['next_page']
        break if next_page.nil?
        error('GitHub pagination did not advance') unless next_page > current_page
        current_page = next_page
      end
      entries
    end,
    # GitHub's /issues endpoint also contains pull requests. Report issues only.
    normalize_issues: lambda do |response|
      response.reject { |item| item.key?('pull_request') }.map do |item|
        {
          'number' => item['number'],
          'title' => item['title'],
          'state' => item['state'],
          'html_url' => item['html_url'],
          'created_at' => item['created_at'],
          'updated_at' => item['updated_at'],
          'author_login' => item['user'].is_a?(Hash) ? item['user']['login'] : nil,
          'labels' => (item['labels'] || []).map do |label|
            { 'name' => label.is_a?(Hash) ? label['name'] : label.to_s }
          end
        }
      end
    end,
    next_page_from_link: lambda do |headers|
      link = headers.is_a?(Hash) ? (headers['link'] || headers['Link']).to_s : ''
      target = link.split(',').find { |part| part.include?('rel="next"') }
      target && target[/[?&]page=(\d+)/, 1]&.to_i
    end
  },

  pick_lists: {
    issue_states: lambda do |_connection|
      [['Open', 'open'], ['Closed', 'closed'], ['All', 'all']]
    end,
    issue_sort: lambda do |_connection|
      [['Last created', 'created'], ['Last updated', 'updated'], ['Most comments', 'comments']]
    end,
    sort_directions: lambda do |_connection|
      [['Newest first', 'desc'], ['Oldest first', 'asc']]
    end,
    # Token-aware repository list includes private repositories accessible to the
    # authenticated account (unlike /users/:owner/repos, which is public only).
    # This uses up to ten 100-result pages and filters by the requested owner.
    owner_repositories: lambda do |_connection, owner:|
      selected_owner = call('validate_slug', owner, 'Repository owner')
      repositories = call('fetch_picklist_pages', '/user/repos',
        { sort: 'full_name', direction: 'asc' }, 10)
      repositories
        .select do |repo|
          repo['owner'].is_a?(Hash) &&
            repo['owner']['login'].to_s.downcase == selected_owner.downcase
        end
        .map { |repo| [repo['name'], repo['name']] }
        .uniq
        .sort_by { |option| option[0].downcase }
    end,
    # Repository-specific label choices; bounded at 1,000 entries.
    repository_labels: lambda do |_connection, owner:, repo:|
      selected_owner = call('validate_slug', owner, 'Repository owner')
      selected_repo = call('validate_slug', repo, 'Repository name')
      labels = call('fetch_picklist_pages',
        "/repos/#{selected_owner}/#{selected_repo}/labels", {}, 10)
      labels.map { |label| [label['name'], label['name']] }.uniq
    end
  },

  object_definitions: {
    issues_response: {
      fields: lambda do
        [
        { name: 'repository', type: 'string' },
        { name: 'page', type: 'integer' },
        { name: 'next_page', type: 'integer', optional: true },
        { name: 'has_more', type: 'boolean' },
        { name: 'count', type: 'integer' },
        {
          name: 'issues', type: 'array', of: 'object', properties: [
            { name: 'number', type: 'integer' },
            { name: 'title', type: 'string' },
            { name: 'state', type: 'string' },
            { name: 'html_url', type: 'string' },
            { name: 'created_at', type: 'date_time' },
            { name: 'updated_at', type: 'date_time' },
            { name: 'author_login', type: 'string' },
            {
              name: 'labels', type: 'array', of: 'object', properties: [
                { name: 'name', type: 'string' }
              ]
            }
          ]
        }
        ]
      end
    }
  },

  actions: {
    list_repository_issues: {
      title: 'List repository issues',
      subtitle: 'Browse issues with filters, dependent picklists, and page navigation',
      description: 'List issues from a GitHub repository without modifying any data.',
      help: 'Read-only. Fetches one GitHub API page (1-100 raw items), which can include pull requests. ' \
            'Pull requests are excluded from output, so count may be less than Items per page. ' \
            'Follow Next page until has_more is false.',
      input_fields: lambda do |_object_definitions|
        [
          { name: 'owner', label: 'Repository owner', type: 'string', optional: false,
            hint: 'GitHub username or organization, e.g. octocat.' },
          { name: 'repo', label: 'Repository', type: 'string', optional: false,
            control_type: 'select', pick_list: 'owner_repositories',
            pick_list_params: { owner: 'owner' },
            hint: 'Lists token-accessible repositories for this owner (first 1,000 accessible repos). ' \
                  'If a repository is missing, verify token access.' },
          { name: 'state', label: 'Issue state', type: 'string', control_type: 'select',
            pick_list: 'issue_states', optional: true, default: 'open', sticky: true },
          { name: 'sort', label: 'Sort by', type: 'string', control_type: 'select',
            pick_list: 'issue_sort', optional: true, default: 'updated' },
          { name: 'direction', label: 'Sort direction', type: 'string', control_type: 'select',
            pick_list: 'sort_directions', optional: true, default: 'desc' },
          { name: 'label', label: 'Filter by label', type: 'string', optional: true,
            control_type: 'select', pick_list: 'repository_labels',
            pick_list_params: { owner: 'owner', repo: 'repo' },
            hint: 'Labels for the selected repository; first 1,000 labels.' },
          { name: 'page', label: 'Page', type: 'integer', control_type: 'number',
            optional: true, default: 1, hint: 'Use Next page from the previous result.' },
          { name: 'per_page', label: 'Items per page', type: 'integer', control_type: 'number',
            optional: true, default: 30, hint: 'Between 1 and 100.' }
        ]
      end,
      execute: lambda do |_connection, input|
        owner = call('validate_slug', input['owner'], 'Repository owner')
        repo = call('validate_slug', input['repo'], 'Repository name')
        page = call('positive_integer', input['page'], 1, 10_000, 'Page')
        per_page = call('positive_integer', input['per_page'], 30, 100, 'Items per page')
        state = input['state'].to_s.empty? ? 'open' : input['state']
        sort = input['sort'].to_s.empty? ? 'updated' : input['sort']
        direction = input['direction'].to_s.empty? ? 'desc' : input['direction']
        error('Invalid issue state') unless %w[open closed all].include?(state)
        error('Invalid sort value') unless %w[created updated comments].include?(sort)
        error('Invalid direction') unless %w[asc desc].include?(direction)
        query = { state: state, sort: sort, direction: direction,
                  page: page, per_page: per_page }
        label = input['label'].to_s.strip
        query[:labels] = label unless label.empty?

        get("/repos/#{owner}/#{repo}/issues")
          .params(query)
          .after_error_response(/.*/) do |code, body, headers, _message|
            error(call('github_error', code, body, headers))
          end
          .after_response do |_code, body, headers|
            error('Unexpected GitHub response; expected a list of issues') unless body.is_a?(Array)
            issues = call('normalize_issues', body)
            next_page = call('next_page_from_link', headers)
            {
              'repository' => "#{owner}/#{repo}",
              'page' => page,
              'next_page' => next_page,
              'has_more' => !next_page.nil?,
              'count' => issues.length,
              'issues' => issues
            }
          end
      end,
      output_fields: lambda do |object_definitions|
        object_definitions['issues_response']
      end,
      sample_output: lambda do |_connection, _input|
        {
          repository: 'octocat/Hello-World', page: 1, next_page: nil,
          has_more: false, count: 1,
          issues: [{ number: 1, title: 'Demo issue', state: 'open',
                     html_url: 'https://github.com/octocat/Hello-World/issues/1',
                     author_login: 'octocat', labels: [{ name: 'documentation' }] }]
        }
      end,
      retry_on_response: [500, 502, 503, 504],
      retry_on_request: ['GET'],
      max_retries: 2,
      summarize_output: ['issues']
    }
  }
}
