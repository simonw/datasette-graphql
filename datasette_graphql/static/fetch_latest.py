import httpx

urls = (
    "https://unpkg.com/react/umd/react.production.min.js",
    "https://unpkg.com/react-dom/umd/react-dom.production.min.js",
    "https://unpkg.com/graphiql/graphiql.min.css",
    "https://unpkg.com/graphiql/graphiql.min.js",
)


def fetch(url):
    final_url = httpx.get(url).next_request.url
    content = httpx.get(final_url).text
    version = str(final_url).split("@")[1].split("/")[0]
    filename = str(final_url).split("/")[-1]
    # Insert version into filename
    bits = filename.split(".min.")
    version_filename = f".{version}.min.".join(bits)
    open(version_filename, "w").write(content)
    print(version_filename)


if __name__ == "__main__":
    for url in urls:
        fetch(url)
