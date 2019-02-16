from libs import plugin, embed
import discord, traceback, asyncio
import logging
from os import getcwd

def errorLogging():
    '''() -> Logger class
    set ups main log so that it outputs to errors.log and then returns the log'''
    logger = logging.getLogger('errors')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='errors.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    return logger

log = errorLogging()

class Plugin(plugin.AdminPlugin):
    '''Dummy plugin for modifying the error catching methods of the bot.
    The methods are modified in order to send PMs to the owner of the add-on'''
    def on_client_add(self):
        self.bot.on_command_error=self.on_command_error
        self.bot.on_reaction_add_error=self.bot.on_reaction_remove_error=self.on_reaction_error
        for name in self.bot.plugins:
            plugin = self.bot.plugins[name]
            plugin.on_action_error = lambda e : self.on_plugin_error(str(name), e)

    @asyncio.coroutine
    def on_command_error(self, cmd_name, error, message):
        log.error(error)
        if isinstance(error, discord.DiscordException):
            keys_list = list(self.bot.commands.keys())
            if cmd_name == keys_list[-1] and 'invalid' in keys_list[-1].lower():
                return
            log.info("Caught discord exception in %s" % cmd_name)
            error_msg = self.make_dis_error_str(error, cmd_name)
            try:
                yield from self.send_message(message.channel, error_msg)
            except discord.Forbidden:
                try:
                    yield from self.send_message(message.author, error_msg)
                except discord.Forbidden:
                    log.warning("Sending discord error failed during exception in %s" % cmd_name)
            return

        package = self.get_package(cmd_name, self.bot.COMMANDS)
        if not package:
            type = self.public_namespace.COMMANDS
            name = cmd_name
        else:
            type = self.public_namespace.PACKAGES
            name = package
        if name not in self.public_namespace.commanders[type]:
            commanders2 = self.public_namespace.generate_commanders(self.bot)
            self.public_namespace.merge_commanders(commanders2)
        user_id = self.public_namespace.commanders[type][name][self.public_namespace.OWNER]
        user = discord.utils.find(lambda u: u.id == user_id, self.bot.get_all_members())
        if user:
            tb = self.make_traceback(error)
            title = '**%s** (command) raised an exception during execution' %cmd_name
            desc = '```'+tb+'```'
            desc+= '**message.content**```%s```' %message.content
            footer = {'text':'You are receiving this because your are the registered owner of this %s' %type[:-1], 'icon_url':None}
            em = embed.create_embed(footer=footer, title=title, description=desc, colour=0xff1111)
            try:
                yield from self.send_message(user, embed=em)
            except:
                traceback.print_exc()
                pass

    @asyncio.coroutine
    def on_reaction_error(self, cmd_name, error, reaction, user):
        log.error(error)
        if isinstance(error, discord.DiscordException):
            keys_list = list(self.bot.reactions.keys())
            if cmd_name == keys_list[-1] and 'invalid' in keys_list[-1].lower():
                return
            log.info("Caught discord exception in %s" % cmd_name)
            error_msg = self.make_dis_error_str(error, cmd_name)
            try:
                yield from self.send_message(reaction.message.channel, error_msg)
            except discord.Forbidden:
                try:
                    yield from self.send_message(user, error_msg)
                except discord.Forbidden:
                    log.warning("Sending discord error failed during exception in %s" % cmd_name)
            return

        package = self.get_package(cmd_name, self.bot.REACTIONS)
        if not package:
            type = self.public_namespace.REACTIONS
            name = cmd_name
        else:
            type = self.public_namespace.PACKAGES
            name = package
        if name not in self.public_namespace.commanders[type]:
            commanders2 = self.public_namespace.generate_commanders(self.bot)
            self.public_namespace.merge_commanders(commanders2)
        user_id = self.public_namespace.commanders[type][name][self.public_namespace.OWNER]
        user = discord.utils.find(lambda u: u.id == user_id, self.bot.get_all_members())
        if user:
            tb = self.make_traceback(error)
            title = '**%s** (reaction) raised an exception during execution' %cmd_name
            desc = '```'+tb+'```'
            footer = {'text':'You are receiving this because you are the registered owner of this %s' %type[:-1], 'icon_url':None}
            em = embed.create_embed(footer=footer, title=title, description=desc, colour=0xff1111)
            try:
                yield from self.send_message(user, embed=em)
            except:
                traceback.print_exc()
                pass

    def on_plugin_error(self, cmd_name, error):
        package = self.get_package(cmd_name, self.bot.PLUGINS)
        if not package:
            type = self.public_namespace.PLUGINS
            name = cmd_name
        else:
            type = self.public_namespace.PACKAGES
            name = package
        if name not in self.public_namespace.commanders[type]:
            commanders2 = self.public_namespace.generate_commanders(self.bot)
            self.public_namespace.merge_commanders(commanders2)
        user_id = self.public_namespace.commanders[type][name][self.public_namespace.OWNER]
        user = discord.utils.find(lambda u: u.id == user_id, self.bot.get_all_members())
        if user:
            tb = self.make_traceback(error)
            title = '**%s** (plugin) raised an exception during execution' %cmd_name
            desc = '```'+tb+'```'
            footer = {'text':'You are receiving this because you are the registered owner of this %s' %type[:-1], 'icon_url':None}
            em = embed.create_embed(footer=footer, title=title, description=desc, colour=0xff1111)
            self.bot.loop.create_task(self.send_message(user, embed=em))

    def get_package(self, cmd_name, addon_type):
        for package in self.bot.packages:
            if cmd_name in self.bot.packages[package][addon_type]:
                return package

    def make_dis_error_str(self, error, name):
        if isinstance(error, discord.Forbidden):
            result = 'Missing permissions to do that while executing `%s`.' % name
        elif isinstance(error, discord.NotFound):
            result = 'Failed to find something while executing `%s`.' % name
        elif isinstance(error, discord.HTTPException):
            result = 'An HTTP issue occured in `%s`.' % name
        else:
            result = 'An unknown error occured in `%s`' % name
        result += ' If this is an error, please contact the developer ```%s``` ' % str(error)
        return result

    def make_traceback(self, err):
        tb = ''.join(traceback.format_exception(type(err), err, err.__traceback__))
        tb = tb.replace(str(getcwd()), '') # remove folder leaks
        return tb
