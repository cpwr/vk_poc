import os

import vk

from dotenv import load_dotenv

load_dotenv()


class VKClient:

    def __init__(self, client: vk.API):
        self.client = client

    def get_user_by_id(self, user_id: int) -> dict:
        return self.client.users.get(user_id=user_id)

    def get_users_by_id(self, user_ids: list[int]) -> list[dict]:
        return self.client.users.get(user_ids=user_ids)

    def get_group_by_id(self, group_id: str | int) -> dict:
        return self.client.groups.getById(group_id=group_id)[0]

    def get_groups_by_id(self, group_ids: list[str | int]) -> list[dict]:
        return self.client.groups.getById(group_ids=group_ids)

    def get_group_members(self, group_id: str | int) -> dict:
        return self.client.groups.getMembers(group_id=group_id)

    def get_user_subs(self, user_id: int):
        return self.client.users.getSubscriptions(user_id=user_id)

    def get_group_topics(self, group_id: int):
        return self.client.board.getTopics(group_id=group_id)

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
        )

    def get_obj_posts(
        self,
        owner_id: int,  # user_id | group_id [should be prefixed with -]
        domain: str,
        offset: int,
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
        )


def save_data(data, filename="data.txt"):
    pass


def enter_data(filename="data.txt"):
    pass


if __name__ == "__main__":
    token = os.getenv("service_key")
    vk_api = vk.API(access_token=token, v='5.131')
    client = VKClient(client=vk_api)

    print(client.get_user_by_id(user_id=1))  # get user
    group_id = client.get_group_by_id(group_id="1")["id"]  # get group info
    # print(group_id, "group_id")
    followers = client.get_group_members(group_id)  # get group members
    # print(followers, "followers")
    # print(client.get_users_by_id(user_ids=followers["items"]))
    subs = client.get_user_subs(user_id=1)
    print(subs, "subs")
