require 'jekyll/tagging'

# Monkey patch of the changes to jekyll-tagging from
# https://github.com/pattex/jekyll-tagging/pull/36

module Jekyll
    module Filters

        def tag_url(tag, type = :page, site = Tagger.site)
            url = File.join('', "#{site.config["baseurl"]}/#{site.config["tag_#{type}_dir"]}", ERB::Util.u(tag))
            site.permalink_style == :pretty || site.config['tag_permalink_style'] == 'pretty' ? url << '/' : url << '.html'
        end

    end
end
