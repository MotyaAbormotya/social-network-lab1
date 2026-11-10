class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


class Post:
    def __init__(self, id: int, author_id: int, text: str):
        self.id = id
        self.author_id = author_id
        self.text = text


class Comment:
    def __init__(self, id: int, post_id: int, author_id: int, text: str):
        self.id = id
        self.post_id = post_id
        self.author_id = author_id
        self.text = text


class NetworkError(Exception):
    pass


Record = User | Post | Comment
Data = dict[str, dict[int, Record]]
TYPES = {
    "users": (User, ("name",)),
    "posts": (Post, ("author_id", "text")),
    "comments": (Comment, ("post_id", "author_id", "text")),
}
