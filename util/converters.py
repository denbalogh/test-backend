from werkzeug.routing import BaseConverter

class StringListConverter(BaseConverter):
    regex = r'.+(?:,.+)*,?'

    def to_python(self, value):
        return [x for x in value.split(',')]
    
    def to_url(self, value):
        return ",".join(str(x) for x in value)