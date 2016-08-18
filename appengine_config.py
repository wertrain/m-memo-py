"""`appengine_config` gets loaded when starting a new application instance."""
import vendor
# insert `lib` as a site directory so our `main` module can load
# third-party libraries, and override built-ins with newer
# versions.
vendor.add('lib')
vendor.add('lib/bottle-0.11.6')
vendor.add('lib/jinja2-2.7.3')
vendor.add('lib/short_url')
vendor.add('lib/markdown-2.6.2')
vendor.add('lib/bleach-1.4.1')
vendor.add('lib/html5lib-0.99999') # for bleach
vendor.add('lib/six-1.9.0') # for bleach