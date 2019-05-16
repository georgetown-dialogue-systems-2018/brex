inform = {
    "book": [
        {"text": """Have you read '{book}'?""",
         "suggestions": ["No, what's it about?",
                         "Yes, I have"]},
        {"text": """I read '{book}' last week, and highly recommend it!""",
         "suggestions": []},
        {"text": """'{book}' is quite nice. It's one of the first ones dad gave to me in the lab.""",
         "suggestions": []},
        {"text": """I'm a big fan of '{book}'. Have you heard of it before?""",
         "suggestions": []},
        {"text": """Let's see, have you ever heard of '{book}'?""",
         "suggestions": []},
        {"text": """Well then, you have a look at '{book}'!""",
         "suggestions": []},
        {"text": """You should read '{book}'. Have you read this one before?""",
         "suggestions": []},
        {"text": """Let's see. How about '{book}'?""",
         "suggestions": []},
        {"text": """Okay, I would recommend '{book}'.""",
         "suggestions": []},
        {"text": """'{book}' would be a good option. Have you read this one before?""",
         "suggestions": []},
        {"text": """'{book}' is still on my to-read list, but I would recommend it! I've heard great things from my book club.""",
         "suggestions": []},
        {"text": """Based on what a good friend has told me, '{book}' is a pretty good read. Have you read this one?""",
         "suggestions": []},
        {"text": """Hmm, alright, I would recommend '{book}'. Have you read it before?""",
         "suggestions": []},
        {"text": """I think '{book}' would be good for that. In fact, I read it last year. Have you read it before?""",
         "suggestions": []},
        {"text": """Oh, we just read '{book}' the other week in the club. Have you read it before?""",
         "suggestions": []},
        {"text": """'{book}' is a real page-turner, even though it's difficult to turn pages with little arms like mine. Have you read it before?""",
         "suggestions": []},
        {"text": """You might want to look at '{book}', it's a real hit among the stegosauruses.""",
         "suggestions": []},
        {"text": """For that, others I've talked to have really liked '{book}'. Have you heard of it?""",
         "suggestions": []},
    ],
    # failure
    "none_found_by_author": [
        {"text": """I can't seem to think of any books written by {author}. Is there someone else you're interested in?""",
"suggestions": []}
    ],
    "none_found_by_genre": [
        {"text": """{genre}... Unfortunately, that's a genre I'm still ignorant of. Is there another you like?""",
"suggestions": []}
    ],
    "book_list_exhausted": [
        {"text": """That's just about all the books I know about in this area. Maybe there's another genre or author you like?""",
"suggestions": []}
    ],
    "no_generating_entities": [
        {"text": """I don't quite understand what kind of book you're interested in. Is there a genre or author you like?""",
         "suggestions": []}
    ]
}
