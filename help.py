import re
from libs import command, embed

HELP_HELPSTRING = '''
Use this command to show the usage instructions for a command, reaction-command or plugin (ie any add-on).

**Usage**
```@Idea help <add-on> [<add-on type>]```
Where
**`<add-on>`** is any command/reaction-command/plugin
**`<add-on type>`** is -c, -r, -l or nothing to indicate whether `<add-on>` is a command/reaction-command/plugin/ambiguous
*(respectively)*

**Example**
`@Idea help perms_setter`

To see the list of commands/reaction-commands/plugins, use:
```@Idea help (commands/reactions/plugins)```
*(respectively)*

If you're really stuck, ask for help from the devs: https://discord.gg/gwq2vS7
'''

VERBOSE_HELPSTRING = '''Verbosity verboses verb very verbosily'''

MULTIPLE_RESULTS = '''
Multiple matches for that command found.
To specify between reaction-command, command and plugin use `-r`, `-c` and `-l`
*(respectively)*
'''

FIRST_LETTER_BLACKLIST=['!', '?', '<']

class Command(command.AdminCommand, command.DirectOnlyCommand):
    def matches(self, message):
        return self.collect_args(message)!=None

    def action(self, message, client):
        send_func = self.send_message
        args = self.collect_args(message)
        response_channel = message.author if '-p' not in message.content else message.channel

        is_verbose = '-v' in message.content
        has_flag = '-c' in message.content or '-r' in message.content or '-l' in message.content

        if not args.group(1):
            help = self.make_help('', self._help(verbose=is_verbose))
            foot_text = 'Bot maintained by NGnius'
            help.set_footer(text=foot_text)
            yield from send_func(response_channel, embed=help)
            return

        is_reaction = args.group(1) in client.reactions
        is_command = args.group(1) in client.commands
        is_plugin = args.group(1) in client.plugins
        is_two = (is_reaction + is_command + is_plugin) > 1
        end_of_message = re.sub(r'-\b\w\b', '', args.group(2)) if args.group(2) is not None else ''

        if is_two and not has_flag:
            yield from send_func(response_channel, MULTIPLE_RESULTS)

        elif is_command and (not is_two or ('-c' in message.content and is_two)):
            help = self.make_help(args.group(1), client.commands[args.group(1)]._help(end_of_message, verbose=is_verbose))
            pkg = client.get_package(args.group(1), client.COMMANDS)
            if pkg!=None:
                addon_type=self.public_namespace.PACKAGES
                addon_name=pkg
            else:
                addon_type=self.public_namespace.COMMANDS
                addon_name=args.group(1)
            if args.group(1) not in self.public_namespace.commanders[addon_type]:
                commanders = self.public_namespace.generate_commanders(client)
                self.public_namespace.merge_commanders(commanders)
            foot_text = 'Command made by '+(yield from client.get_user_info(self.public_namespace.commanders[addon_type][addon_name][self.public_namespace.OWNER])).name
            help.set_footer(text=foot_text)
            yield from send_func(response_channel, embed=help)

        elif is_reaction and (not is_two or ('-r' in message.content and is_two)):
            help = self.make_help(args.group(1), client.reactions[args.group(1)]._help(end_of_message, verbose=is_verbose))
            pkg = client.get_package(args.group(1), client.REACTIONS)
            if pkg!=None:
                addon_type=self.public_namespace.PACKAGES
                addon_name=pkg
            else:
                addon_type=self.public_namespace.REACTIONS
                addon_name=args.group(1)
            if args.group(1) not in self.public_namespace.commanders[self.public_namespace.REACTIONS]:
                commanders = self.public_namespace.generate_commanders(client)
                self.public_namespace.merge_commanders(commanders)
            foot_text = 'Reaction made by '+(yield from client.get_user_info(self.public_namespace.commanders[addon_type][addon_name][self.public_namespace.OWNER])).name
            help.set_footer(text=foot_text)
            yield from send_func(response_channel, embed=help)

        elif is_plugin and (not is_two or ('-l' in message.content and is_two)):
            help = self.make_help(args.group(1), client.plugins[args.group(1)]._help(end_of_message, verbose=is_verbose))
            pkg = client.get_package(args.group(1), client.PLUGINS)
            if pkg!=None:
                addon_type=self.public_namespace.PACKAGES
                addon_name=pkg
            else:
                addon_type=self.public_namespace.PLUGINS
                addon_name=args.group(1)
            if args.group(1) not in self.public_namespace.commanders[self.public_namespace.PLUGINS]:
                commanders = self.public_namespace.generate_commanders(client)
                self.public_namespace.merge_commanders(commanders)
            foot_text = 'Plugin made by '+(yield from client.get_user_info(self.public_namespace.commanders[addon_type][addon_name][self.public_namespace.OWNER])).name
            help.set_footer(text=foot_text)
            yield from send_func(response_channel, embed=help)

        elif args.group(1).lower() in self.ADDON_TYPE_LIST:
            # list addons of that type
            addon_type = get_type(args.group(1))
            addons = eval("client."+addon_type)
            addons_dict=dict()
            for i in addons:
                pkg = client.get_package(i, addon_type)
                if pkg not in addons_dict:
                    addons_dict[pkg]=list()
                addons_dict[pkg].append(i)

            em = make_embed(addons_dict)
            em.title = 'My '+addon_type
            yield from self.send_message(response_channel, embed=em)

        else:
            yield from send_func(response_channel, 'Add-on not found')

    def collect_args(self, message):
        return re.search(r'help\b(?:\sme)?(?:\swith)?(?:\s([^\-\s]\S*))?(?:\s+(.*))?', message.content, re.I)

    def make_help(self, name, docstring):
        description = '%s Help\n' % name
        em = embed.create_embed(title=description, description=docstring, colour=0xff00ff)
        return em

    def help(self, *args, verbose=False, **kwargs):
        if verbose:
            return VERBOSE_HELPSTRING
        return HELP_HELPSTRING

def process_list(iter, prefix='', suffix=''):
    result = ''
    for i in iter:
        if str(i)[0] not in FIRST_LETTER_BLACKLIST and passes_filter(str(i)):
            result+=prefix+str(i)+suffix+'\n'
    return result

def make_embed(addons_dict, colour=0xff00ff):
    footer={'text':'@Idea help <item> for more info', 'icon_url':None}
    desc = ''
    for key in addons_dict:
        if key is not None: # display package-less add-ons at the bottom
            desc+='**'+key+'**'+'\n'
            desc+=process_list(addons_dict[key], prefix='--')
    if None in addons_dict:
        desc+='**'+'[NO PACKAGE]'+'**'+'\n'
        desc+=process_list(addons_dict[None], prefix='--')
    em = embed.create_embed(description=desc, footer=footer, colour=colour)
    return em


def passes_filter(string):
    return re.match(r'(.)\1*\_', string) is None

def get_type(string):
    return string.lower().rstrip('s')+'s'
