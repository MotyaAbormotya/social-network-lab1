from application.network_service import NetworkService
from infrastructure.file_repository import FileRepository
from presentation.console import run


def main():
    repository = FileRepository()
    service = NetworkService(repository)
    run(service)


if __name__ == "__main__":
    main()
