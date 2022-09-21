'''
File just to store regex dictionary config, will depricate
'''

REGEX = {
        "username": r"^[\w\._]+$",
        "phone": r"^01\d{9}",
        "email": r"^[^\.\s\n\\][^\n\s\\]*@[^\.\s\n\\]+\.[^\.\s\n\\]+",
        "password": r"^.{8,52}$",
        "speed": r"^\d{2}$",
        "distance": r"^\d{1,3}$",
        "arabic" : r"[\u0600-\u06FF]+"
        }

