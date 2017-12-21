from html.parser import HTMLParser
from html.entities import name2codepoint


""" Parser for remove html entities from string, and detect if a text has html entities

Example:
    html = "<h1>titulo</h1> welcome to <a href='google.com'>google.com</a>"
    parser = MyHTMLParser()
    parser.feed(html)
    print(parser.get_plain_text())
    print(parser.is_html())

"""
class MyHTMLParser(HTMLParser):

    data = []
    star_tag = []
    end_tag = []
    comments = []
    convert_charrefs = True

    def __init__(self):
        self.reset()
        self.data = []
        self.star_tag = []
        self.end_tag = []
        self.comments = []
        self.convert_charrefs = True

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            self.star_tag.append(attr)

    def handle_endtag(self, tag):
        self.end_tag.append(tag)

    def handle_data(self, data):
        self.data.append(data)

    def handle_comment(self, data):
        self.comments.append(data)

    # def handle_entityref(self, name):
    #     c = chr(name2codepoint[name])
    #     print("Named ent:", c)

    # def handle_charref(self, name):
    #     if name.startswith('x'):
    #         c = chr(int(name[1:], 16))
    #     else:
    #         c = chr(int(name))
    #     print("Num ent  :", c)

    # def handle_decl(self, data):
    #     print("Decl     :", data)

    def get_plain_text(self):
        result = ''
        for d in self.data:
            result += "{}".format(d)
        return result.replace(u'\xa0', u' ')

    def is_html(self):
        return len(self.star_tag) + len(self.end_tag) > 0
