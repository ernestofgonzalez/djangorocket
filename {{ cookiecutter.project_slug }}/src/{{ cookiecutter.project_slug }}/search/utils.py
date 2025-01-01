from django_opensearch_dsl.search import Search


def search(query, course_uuid=None):
    search = Search(index="exercises")
    search = search.query(
        "multi_match",
        query=query,
        fields=[
            "content_name^3",
            "content_messages_text^2",
            "content_messages_text_translation",
        ],
        fuzziness="AUTO",
    )

    if course_uuid:
        search = search.filter("term", course_uuid=course_uuid)

    return search.execute()
