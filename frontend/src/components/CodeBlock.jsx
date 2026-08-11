
  import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
  import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";

  export default function CodeBlock({ code, language }) {
    return (
      <div className="rounded-lg overflow-hidden border border-gray-200 text-sm">
        <SyntaxHighlighter language={language || "javascript"} style={oneLight} customStyle={{ margin: 0, padding: "1rem" }}>
          {code}
        </SyntaxHighlighter>
      </div>
    );
  }