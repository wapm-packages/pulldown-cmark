const { bindings } = require("@wasmer/pulldown-cmark");
const {
  Options,
  OffsetItem,
  OPTIONS_ENABLE_STRIKETHROUGH,
} = require("@wasmer/pulldown-cmark/src/bindings/pulldown/pulldown.js");

test("Test Markdown to Html", async () => {
  const wasm = await bindings.pulldown();
  const markdownString = String.raw`
hello
=====
* alpha
* beta
`;
  const htmlString = wasm.markdownToHtml(markdownString);
  const resultString = String.raw`<h1>hello</h1>
<ul>
<li>alpha</li>
<li>beta</li>
</ul>
`;
  expect(htmlString).toBe(resultString);
});

test("Test Parser with StrikeThrough Option", async () => {
  const wasm = await bindings.pulldown();
  const markdownString = String.raw`Hello world, this is a ~~complicated~~ *very simple* example.`;
  const strikethroughOption = OPTIONS_ENABLE_STRIKETHROUGH;

  const iters = wasm.parseWithOptions(markdownString, strikethroughOption);

  console.dir(iters, { depth: null });

  expect(iters).toBeInstanceOf(Array);
});
