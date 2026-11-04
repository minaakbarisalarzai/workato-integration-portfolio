"""Optional template-copy contract; disabled unless deployment has vendor validation.

The original academic implementation used Workato export manifests and imports.
The actual Workato API version, authentication scope, and async semantics MUST be
revalidated before implementing against a live tenant. Fail closed by default.
"""
class FeatureNotVerified(RuntimeError):
    pass


def copy_template_assets(*, enabled=False, **_kwargs):
    if not enabled:
        raise FeatureNotVerified('template_copy_disabled_pending_live_api_verification')
    raise FeatureNotVerified('template_copy_requires_current_workato_api_contract_validation')
