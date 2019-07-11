import sphinx_rtd_theme
import remt

extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.doctest',
    'sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.mathjax'
]
project = 'remt'
source_suffix = '.rst'
master_doc = 'index'

version = release = atimer.__version__
copyright = 'remt team'

epub_basename = 'remt - {}'.format(version)
epub_author = 'remt team'

todo_include_todos = True

html_theme = 'sphinx_rtd_theme'
html_static_path = ['static']
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_style = 'remt.css'


# vim: sw=4:et:ai
