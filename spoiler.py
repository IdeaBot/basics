from libs import command
from libs import embed
import re

class Command(command.DirectOnlyCommand):
    '''A bit of spam never hurt anyone

**Usage**
To get a message warning about spoilers above, with <number> blank lines above it
```@Idea spoiler <number>```

**__WARNING:__** This command will be removed with the next point release (v1.0) Use Discord\'s built in spoilers instead '''
    def matches(self, message):
        args = re.search(r'\bspoiler\s([\d]{1,2})', message.content, re.I)
        return args != None
    def action(self, message):
        args = re.search(r'\bspoiler\s([\d]{1,2})', message.content, re.I)
        msgEmbed = embed.create_embed(title="SPOILERS!", author={"name":"River Song", "url":None, "icon_url":None}, description=int(args.group(1))*".\n"+"^^^ WARNING: Spoiler Above ^^^")
        yield from self.send_message(message.channel, embed=msgEmbed)
