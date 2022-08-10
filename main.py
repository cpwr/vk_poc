import json
import os

from datetime import datetime, timezone
from dataclasses import dataclass
from time import sleep
from typing import Iterable

import requests
import vk

from dotenv import load_dotenv
from yarl import URL

load_dotenv()


@dataclass
class Post:
    id: int
    owner_id: int
    from_id: int
    date: int | None
    edited: int | None
    post_type: str
    text: str
    comments_count: int
    likes_count: int
    reposts_count: int
    views_count: int

    @property
    def date_created(self):
        if self.date:
            return datetime.fromtimestamp(self.date, tz=timezone.utc)

    @property
    def date_edited(self):
        if self.edited:
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

    def iter_search(
        self,
        query: str,
        extended: int = 1,  # will return like user and group info
        offset: int | None = None,
        count: int = 200,
        start_id: int | None = None,
        start_from: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        fields: list | None = None,
    ) -> Iterable:
        batch = self.newsfeed_search(
            query=query,
            extended=extended,
            offset=offset,
            count=count,
            start_id=start_id,
            start_from=start_from,
            start_time=start_time,
            end_time=end_time,
            fields=fields,
        )
        if batch:
            yield batch
            sleep(0.5)

        while next_from := batch.get("next_from"):
            batch = self.newsfeed_search(
                query=query,
                extended=extended,
                offset=offset,
                count=count,
                start_id=start_id,
                start_from=next_from,
                start_time=start_time,
                end_time=end_time,
                fields=fields,
            )
            if batch:
                yield batch
                sleep(0.5)

    def newsfeed_search(
        self,
        query: str,
        extended: int = 1,  # will return like user and group info
        offset: int | None = None,
        count: int = 200,
        start_id: int | None = None,
        start_from: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        fields: list | None = None,
    ):
        batch = self.client.newsfeed.search(
            q=query,
            extended=extended,
            offset=offset,
            count=count,
            start_id=start_id,
            start_from=start_from,
            start_time=start_time,
            end_time=end_time,
            fields=fields,
            lang=self.lang,
        )
        posts = batch.get("items", [])
        if posts:
            return batch

        return {}


def extract_media(attachments: list) -> tuple[list, list, list, list, list]:
    videos = []
    photos = []
    audios = []
    links = []
    docs = []

    if not attachments:
        return videos, photos, audios, links, docs

    for attachment in attachments:
        match attachment.get("type"):
            case "photo":
                photos.extend([x["url"] for x in attachment["photo"]["sizes"]])
            case "video":
                attachment = attachment.get("video")
                owner_id = attachment.get("owner_id")
                attachment_id = attachment.get("id")
                access_key = attachment.get("access_key")
                if access_key:
                    video_id = f"{owner_id}_{attachment_id}_{access_key}"
                else:
                    video_id = f"{owner_id}_{attachment_id}"
                video_url = f"https://vk.com/video?z=video{video_id}"
                videos.append(video_url)
            case "audio":
                attachment = attachment.get("audio")
                if audio_url := attachment.get("url"):
                    audios.append(audio_url)
            case "link":
                links.append(attachment["link"]["url"])
            case "doc":
                if doc := attachment["doc"]:
                    if doc.get("ext") in ["jpg", "jpeg"]:
                        photos.extend([x["src"] for x in doc.get("preview", {}).get("photo", {}).get("sizes", [])])
                    docs.append(doc["url"])
            case _:
                print("!!!!!")
                print(attachment)
                print("!!!!!")

    return videos, photos, audios, links, docs


def write_data(data, filename="data.txt"):
    pass


def read_data(filename="data.txt"):
    pass


def get_post_link(owner_id: str | int, post_id: str | int) -> str:
    match owner_id:
        case int():
            owner_id = abs(owner_id)
        case str():
            owner_id = owner_id

    try:
        group = client.get_group_by_id(group_id=owner_id)
    except Exception as err:
        print(err)
        return ""

    return f"https://vk.com/{group['screen_name']}?w=wall-{group['id']}_{post_id}"


if __name__ == "__main__":
    token = os.getenv("service_key")
    vk_api = vk.API(access_token=token, v='5.131')
    client = VKClient(api=vk_api)

    res = client.iter_search(query="POLARNET", count=20)
    for batch in res:
        posts = batch.get("items", [])
        groups = batch.get("groups", [])
        profiles = batch.get("profiles", [])
        for post in posts:
            channel_id = post["owner_id"]
            post_id = post["id"]
            link = get_post_link(channel_id, post_id)
            videos, photos, *_ = extract_media(post.get("attachments", []))
            print({
                "id": post["id"],
                "text": post["text"],
                "link": link,
                "peer_channel_id": post["owner_id"],
                "channel_id": post["owner_id"],
                "published_at": post.get("date"),
                "updated_at": post.get("updated_at"),
                "images": photos,
                "videos": videos,
                "views": post.get("views", {}).get("count", 0),
                "forwards": post.get("reposts", {}).get("count", 0),
                "replies": post.get("comments", {}).get("count", 0),
                "likes": post.get("likes", {}).get("count", 0),
            })
        break

    # print(client.get_users_by_id(user_ids=[1, 46976392]))  # get user
    # group_id = client.get_group_by_id(group_id="public128394762")["id"]  # get group info
    # print(group_id, "group_id")
    # print("----------------------")
    # followers = client.get_group_members(
    #     group_id,
    #     fields=["bdate", "city"]
    # )  # get group members
    # print(followers, "followers")
    # print(client.get_users_by_id(user_ids=followers["items"]))
    # subs = client.get_user_subs(user_id=-29534144)
    # print(subs, "subs")
    # posts = client.get_posts(owner_id=-group_id, count=1)
    # posts_data = [
    #     Post(
    #         id=post["id"],
    #         owner_id=post["owner_id"],
    #         from_id=post["from_id"],
    #         date=post["date"],
    #         edited=post.get("edited"),
    #         post_type=post["post_type"],
    #         text=post["text"],
    #         comments_count=post.get("comments", {}).get("count", 0),
    #         likes_count=post.get("likes", {}).get("count", 0),
    #         reposts_count=post.get("reposts", {}).get("count", 0),
    #         views_count=post.get("views", {}).get("count", 0),
    #     ) for post in posts["items"]
    # ]
    # print(posts_data[0].to_dict())

