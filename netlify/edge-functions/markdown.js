export default async (request, context) => {
  const accept = request.headers.get("Accept") || "";
  if (!accept.includes("text/markdown")) {
    return context.next();
  }

  const url = new URL(request.url);
  url.pathname = "/index.md";

  const mdResponse = await context.rewrite(url.pathname);

  return new Response(mdResponse.body, {
    status: mdResponse.status,
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
      "Vary": "Accept",
    },
  });
};

export const config = { path: "/" };
