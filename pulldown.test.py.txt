from pulldown_cmark import bindings
from pulldown_cmark.bindings.pulldown import Options, OffsetItem

pulldown_cmark=bindings.pulldown()


def test_markdown_to_html():
    markdown_string="""
hello
=====
* alpha
* beta
"""
    html_string=pulldown_cmark.markdown_to_html(markdown_string)

    assert(html_string,"""<h1>hello</h1>
<ul>
<li>alpha</li>
<li>beta</li>
</ul>
""")

def parser_with_option_strikethrough():
    markdown_string="Hello world, this is a ~~complicated~~ *very simple* example."

    option=Options.ENABLE_STRIKETHROUGH

    iters=pulldown_cmark.parse_with_options(markdown_string,option);
    print(iters)

def html_test():
    markdown_string="""Little header
<script type="text/js">
function some_func() {
console.log("teeeest");
}
function another_func() {
console.log("fooooo");
}
</script>"""

    expected="""<p>Little header</p>
<script type="text/js">
function some_func() {
console.log("teeeest");
}
function another_func() {
console.log("fooooo");
}
</script>"""
    result = pulldown_cmark.markdown_to_html(markdown_string)
    assert(expected,result)