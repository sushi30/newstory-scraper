from datetime import datetime
import os
import jsonpath_ng


def read_blob(client, container_name, blob):
    container_client = client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob)
    download_stream = blob_client.download_blob()
    return download_stream.readall()


def get_bool_from_env(key):
    return os.getenv(key) in ["True", "true", "1", "yes"]


def extract_profile(dictionary):
    extracted = extract_jsonpath("$.data.GraphProfileInfo.info", dictionary)[0]
    return {
        "created_at": extract_jsonpath("$.created_at", dictionary)[0],
        "profile_created_at": datetime.utcfromtimestamp(
            extract_jsonpath("$.data.GraphProfileInfo.created_time", dictionary)[0]
        ),
        "instagram_profile_id": extracted["id"],
        **{
            k: v
            for k, v in extracted.items()
            if k
            in (
                "username",
                "followers_count",
                "biography",
                "following_count",
                "full_name",
                "is_business_account",
                "is_private",
                "posts_count",
                "profile_pic_url",
            )
        },
    }


def get_from_list(iterable: list, index=0, default=None):
    return (iterable[index : index + 1] or [default])[index]


def extract_posts(dictionary):
    posts = extract_jsonpath("$.data.GraphImages", dictionary)[0]
    posts = [
        {
            "taken_at": datetime.utcfromtimestamp(post["taken_at_timestamp"]),
            "instagram_post_id": post["id"],
            "instagram_author_profile_id": extract_jsonpath("$.owner.id", post)[0],
            "caption": get_from_list(
                extract_jsonpath("$.edge_media_to_caption.edges..node.text", post)
            ),
        }
        for post in posts
    ]
    return posts


def extract_jsonpath(expression, dictionary):
    jsonpath_expr = jsonpath_ng.parse(expression)
    return [v.value for v in jsonpath_expr.find(dictionary)]