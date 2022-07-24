import os
from datetime import datetime, timezone
from dataclasses import dataclass

import vk
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Post:
    id: int
    owner_id: int
    from_id: int
    date: int
    edited: int
    post_type: str
    text: str
    comments_count: int
    likes_count: int
    reposts_count: int
    views_count: int

    @property
    def date_created(self):
        return datetime.fromtimestamp(self.date, tz=timezone.utc)

    @property
    def date_edited(self):
        return datetime.fromtimestamp(self.edited, tz=timezone.utc)

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'from_id': self.from_id,
            'date_created': self.date_created,
            'date_edited': self.date_edited,
            'post_type': self.post_type,
            'text': self.text,
            'comments_count': self.comments_count,
            'likes_count': self.likes_count,
            'reposts_count': self.reposts_count,
            'views_count': self.views_count,
        }


class VKClient:

    def __init__(self, api: vk.API, lang="ru"):
        self.client = api
        self.lang = lang  # "ru" | "uk" | "be" | "en" | "es" | "fi" | "de" | "it"

    def get_user_by_id(self, user_id: int | str, fields: list[str] | None = None) -> dict:
        if fields:
            fields = ",".join(fields)
        return self.client.users.get(user_ids=user_id, fields=fields, lang=self.lang)[0]

    def get_users_by_id(self, user_ids: list[int], fields: list[str] | None = None) -> list[dict]:
        if fields:
            fields = ",".join(fields)
        return self.client.users.get(user_ids=user_ids, fields=fields, lang=self.lang)

    def get_group_by_id(
        self,
        group_id: str | int,
        extended: int = 1,
        fields: list[str] | None = None,
    ) -> dict:
        if fields:
            fields = ",".join(fields)
        return self.client.groups.getById(
            group_id=group_id,
            extended=extended,
            fields=fields,
            count=1,
            lang=self.lang,
        )[0]

    def get_groups_by_id(
        self,
        group_ids: list[str | int],
        extended: int = 1,
        fields: list[str] | None = None,
        count: int | None = None,
    ) -> list[dict]:
        if fields:
            fields = ",".join(fields)
        if count is None:
            count = len(group_ids)
        return self.client.groups.getById(
            group_ids=group_ids,
            extended=extended,
            fields=fields,
            count=count,
            lang=self.lang,
        )

    def get_group_members(
        self,
        group_id: str | int,
        fields: list[str] | None = None,
        offset: int = 0,
        count: int = 1000,
    ) -> dict:
        if fields:
            fields = ",".join(fields)
        return self.client.groups.getMembers(
            group_id=group_id,
            offset=offset,
            count=count,
            fields=fields,
            lang=self.lang,
        )

    def get_user_subs(self, user_id: int):
        return self.client.users.getSubscriptions(user_id=user_id, lang=self.lang)

    def get_group_topics(self, group_id: int):
        return self.client.board.getTopics(group_id=group_id, lang=self.lang)

    def get_group_topic_comments(
        self,
        group_id: int,
        topic_id: int,
        start_comment_id: int | None = None,
        offset: int | None = None,
        need_likes: int = 1,
        count: int = 100,    # batch size. max value is 100
        extended: int = 1,   # will return authors info
        sort: str = "desc",  # start from the earliest
    ):
        return self.client.board.getComments(
            group_id=group_id,
            topic_id=topic_id,
            need_likes=need_likes,
            start_comment_id=start_comment_id,
            offset=offset,
            count=count,
            extended=extended,
            sort=sort,
            lang=self.lang,
        )

    def get_posts(
        self,
        owner_id: int | None = None,  # user_id | group_id [should be prefixed with -]
        domain: str | None = None,
        offset: int | None = None,
        count: int = 100,
        filters: str | None = None,  # all | others | owner
        extended: int = 1,  # will return profiles and groups
        fields: str | None = None,  # fields to return from profiles and groups
    ):
        return self.client.wall.get(
            owner_id=owner_id,
            domain=domain,
            offset=offset,
            count=count,
            filter=filters,
            extended=extended,
            fields=fields,
            lang=self.lang,
        )

    def get_post_comments(
        self,
        owner_id: int,  # user_id | group_id [should be prefixed with -]
        post_id: int,
        start_comment_id: int,
        need_likes: int = 1,
        offset: int | None = None,
        count: int = 100,
        sort: str = "asc",  # "asc" | "desc"
        preview_length: int = 0,  # max length of comment
        extended: int = 1,  # will return profiles and groups
        fields: str | None = None,  # fields to return from profiles and groups
        comment_id: int | None = None,  # comment to return comments for
        thread_items_count: int | None = None,  # max elements in thread
    ):
        return self.client.wall.getComments(
            owner_id=owner_id,
            post_id=post_id,
            need_likes=need_likes,
            start_comment_id=start_comment_id,
            offset=offset,
            count=count,
            sort=sort,
            preview_length=preview_length,
            extended=extended,
            fields=fields,
            comment_id=comment_id,
            thread_items_count=thread_items_count,
            lang=self.lang,
        )

    def get_obj_likes_ids(
        self,
        obj_type: str,  # post | comment | photo | audio | video | photo_comment | video_comment | topic_comment
        owner_id: int,  # user_id | app_id | group_id [should be prefixed with -]
        item_id: int,
        filters: str | None = None,  # likes [all] | copies [reposts]
        extended: int = 1,  # will return like owner's info
        offset: int | None = None,
        count: int = 1000,
    ):
        return self.client.likes.getList(
            type=obj_type,
            owner_id=owner_id,
            item_id=item_id,
            filter=filters,
            friends_only=0,
            extended=extended,
            offset=offset,
            count=count,
            skip_own=1,
            lang=self.lang,
        )


def write_data(data, filename="data.txt"):
    pass


def read_data(filename="data.txt"):
    pass


if __name__ == "__main__":
    token = os.getenv("service_key")
    vk_api = vk.API(access_token=token, v='5.131')
    client = VKClient(api=vk_api)

    # print(client.get_users_by_id(user_ids=[1, 46976392]))  # get user
    group_id = client.get_group_by_id(group_id="bogodukhovs")["id"]  # get group info
    # print(group_id, "group_id")
    followers = client.get_group_members(
        group_id,
        fields=["bdate", "city"]
    )  # get group members
    # print(followers, "followers")
    # print(client.get_users_by_id(user_ids=followers["items"]))
    # subs = client.get_user_subs(user_id=-29534144)
    # print(subs, "subs")
    posts = client.get_posts(domain="bogodukhovs", count=1)
    posts_data = [
        Post(
            id=post["id"],
            owner_id=post["owner_id"],
            from_id=post["from_id"],
            date=post["date"],
            edited=post["edited"],
            post_type=post["post_type"],
            text=post["text"],
            comments_count=post.get("comments", {}).get("count", 0),
            likes_count=post.get("likes", {}).get("count", 0),
            reposts_count=post.get("reposts", {}).get("count", 0),
            views_count=post.get("views", {}).get("count", 0),
        ) for post in posts["items"]
    ]
    print(posts_data[0].to_dict())

