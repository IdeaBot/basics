# basics
IdeaBot add-ons package to provide basic functionality, like help messages and permission setting.

## Overview

### Commands
This outlines the functionality of each command.
Use `@Idea help <command name>` to get usage instructions.

* help
> Get helpful info about an add-on

* random
> Generate a random number.

* featurelist
> Get a message about Idea development.

* ping
> PONG

* spoiler
> Create a long message to push spoilers off the screen.

* timezone
> Convert times between timezones.

* setemoji
> Associate an emoji to a command, with help from emoji_setter.

* emoji_setter
> Associate an emoji to a command. See `help emoji_starter` for more information.

* perms_setter
> Give a user permission to use a command.

* ?list *(Deprecated)*
> List available commands, reaction-command or plugins. THIS HAS BEEN INTEGRATED INTO HELP

* !load
> Load or reload an add-on.

* !unload
> Partially disable an add-on by removing it's owners and maintainers.

* ?commanders
> Update owners and maintainers of packages and add-ons, which dictate permissions for loading & unloading.

* !setup *(Dummy)*
> Sets up some things for other add-ons. This does not (directly) offer any functionality to users.

### Other Functions

* error_reporter
> Sends errors to the owner of the add-on through private messages.

# Documentation
Some functions in the basics package offer functionality to all add-ons, not just add-ons within the basics package.
This functionality is explained here.

## Help
I've fallen and I can't get up (I wonder how many times I've made this joke in the documentation...)

### Functionality
Help is designed to provide help information to users.
Help messages are supported by any add-on, and should be implemented by the add-on writer.
Since the help message is a Discord message, it supports Discord markdown.
The easiest way to make a help string is to write a docstring for the your class.

### Usage
Help uses the `help(help_args_str)` function implemented by the all add-ons to generate the helpstring. By default (as implemented in the base add-on class), this returns the docstring of the class, but it can be overriden. To change the behaviour, override the help method in your add-on implementation.

* **help(help_args_str)** : string
> **help_args_str**:
> the rest of the help message.
> E.g. if the help message content is `@Idea help my_command some stuff afterwards`, `help_args_str` will contain `some stuff afterwards`.
> See [UIdea's UI.py](https://github.com/IdeaBot/UIdea/blob/master/UI.py) add-on for an example of how to use this to modify the behaviour.

### A Note on Future-Proofing
Parameters passed to a function may change as features are added, so you should always end the function parameters with `*args, **kwargs` to ensure your function will continue to work in the future.
