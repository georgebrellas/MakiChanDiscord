# Basic bot usage: #
Using *m!* plus a *command*.
*ex:*

Command:
```
m! say Hello world!
```
Bot Output:
```
Hello World!
```
# Commands: #

### Party ###
silly commands made for fun.

**Hi/Bye**: Basic greeting. Takes no arguments.
```
m! hi
```

**say/Sayd**: Repeats after you. 2nd version *(sayd)* deletes your message too.
```
m! say Hello World!
```
*Note: Bellow commands offer different outputs but have almost identical logic.*

**avatar**: Links yours or a tagged user's avatar.

**roast**: Generates a random insult for either you or someone you tag.

**love/hot/perv**: Shows a percentage from 1% to 100% about you or someone you tag related to the command's name.

```
m! command
m! command @ExampleUser#0000
m! command ExampleUser
```

### Coins ###
Coin related commands!

**coins**: Shows a tagged users coins or yours if no user is tagged.
```
m! coins (@ExampleUser#0000)
```
**give**: Gives a user an X amount of keys.
```
m! give @ExampleUser#0000 X
```
**flip**: Flip a coin!
```
m! flip
```

### Player Controls ###
Commands used to control the youtube_dl player.

**play**: Starts playback of specified URL. If no input is given, it resumes whatever's paused.
```
m! play https://example.com/
```
**resume**: Resumes playback. Redundant so it will probably be removed as play does the same.
```
m! resume
```
**pause**: Pauses playback.
```
m! pause
```
**nowplaying**: Tells you the title of whatever's currently playing.
```
m! nowplaying
```
**vol**: Sets the volume of the playback from 1% to 200%.

*WARNING: setting the volume above 100% WILL cause audio distortion!*
```
m! vol 100
```
### Utilities ###
Commands that take no arguments that are made to be helpful.

**list/help**: Lists all currently available commands.

**creds**: Bot and library credits.
```
m! command
```

### Administration ###
**admin**: Gives/revokes admin permission to user.
```
m! admin @ExampleUser#0000
```
