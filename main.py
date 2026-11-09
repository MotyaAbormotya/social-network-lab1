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


def main():
    user = User(1, "Лена")
    post = Post(1, user.id, "Привет!")
    comment = Comment(1, post.id, user.id, "Мой первый комментарий.")
    print(user.name)
    print(post.text)
    print(comment.text)


if __name__ == "__main__":
    main()
