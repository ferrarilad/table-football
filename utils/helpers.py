import base64
import os
import streamlit as st
from streamlit.components.v1 import html
from typing import Union


def clear_cache():
    st.experimental_memo.clear()
    st.experimental_singleton.clear()


def session_values(prefix: str = None) -> dict:
    session = dict(st.session_state)
    params = {}
    for k, v in session.items():
        if prefix is None or k.startswith(prefix):
            params[k] = v

    return {key: params[key] for key in sorted(params.keys())}


def session(key: str, *args, **kwargs):
    if key not in st.session_state and "init" in kwargs:
        st.session_state[key] = kwargs["init"]

    if args:
        st.session_state[key] = args[0]
    elif "value" in kwargs:
        st.session_state[key] = kwargs["value"]

    return st.session_state[key]


def hide_sidebar():
    html(
        f"""
    <script type="text/javascript">
        var sidebar = window.parent.document.querySelectorAll('[data-testid="stSidebar"]')[0];
        sidebar.style.display = "none";
    </script>
    """,
        width=None,
        height=0,
        scrolling=False,
    )


def show_sidebar():
    html(
        f"""
    <script type="text/javascript">
        var sidebar = window.parent.document.querySelectorAll('[data-testid="stSidebar"]')[0];
        sidebar.style.display = "block";
    </script>
    """,
        width=None,
        height=0,
        scrolling=False,
    )


def refresh():
    html(
        """
    <script type="text/javascript">
        window.location.reload(true);
    </script>"""
    )


def open_link(url: str, target: str = "_blank"):
    html(
        f"""
<script type="text/javascript">
    window.open("{url}", "{target}").focus();
</script>
    """,
        width=None,
        height=0,
        scrolling=False,
    )


def redirect(url: str):
    st.markdown(
        f"""
    <a href="{url}" id="redirect-button" target="_self">Redirect to {url}</a>
    """,
        unsafe_allow_html=True,
    )

    html(
        """
    <script type="text/javascript">
    (function() {
        window.top.document.getElementById("redirect-button").click()
    })();
    </script>
    """,
        width=None,
        height=0,
        scrolling=False,
    )


def download_file(f: str):
    filename = os.path.basename(f)

    with open(f, "rb") as f:
        return download_string_as_file(f.read(), filename)


def download_string_as_file(contents: Union[str, bytes], file_name: str):
    stream_type = "application/octet-stream"

    if isinstance(contents, str):
        contents = contents.encode("utf-8")
    encoded = base64.b64encode(contents)

    html(
        """<script type="text/javascript">
    function downloadBase64File(contentType, base64Data, fileName) {
         const linkSource = `data:${contentType};base64,${base64Data}`;
         const downloadLink = document.createElement("a");
         downloadLink.href = linkSource;
         downloadLink.download = fileName;
         downloadLink.click();
    }

    downloadBase64File("%s", "%s", "%s")
    </script>"""
        % (stream_type, encoded.decode("utf-8"), file_name),
        width=None,
        height=0,
        scrolling=False,
    )
