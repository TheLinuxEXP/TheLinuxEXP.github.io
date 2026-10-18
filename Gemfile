source "https://rubygems.org"

# Plain Jekyll 4 (no github-pages gem): the site is built by GitHub Actions
# (.github/workflows/pages.yml), so gems can be updated freely with
# `bundle update` or Dependabot.
gem "jekyll", "~> 4.4"

group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-paginate"
  gem "jekyll-redirect-from"
  gem "jekyll-sitemap"
end

# Needed by `jekyll serve` on Ruby 3+
gem "webrick"
