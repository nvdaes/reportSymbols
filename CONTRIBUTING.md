# Contributing #

These guidelines are based on the [Contributing to NVDA](https://github.com/nvaccess/nvda/wiki/Contributing) document.

## Request changes ##

For anything other than minor bug fixes, please comment on an existing issue or create a new issue providing details about your proposed change. Unrelated changes should be addressed in separate issues. Include information about use cases, design, user experience, etc. This allows us to discuss these aspects and any other concerns that might arise, thus potentially avoiding a great deal of wasted time. 

If this is a minor/trivial change which definitely wouldn't require design, user experience or implementation discussion (e.g. a fix for a typo/obvious coding error), you can just create a pull request rather than using an issue first. 

## Make changes ##

### If this is your first contribution ###

1. Fork the add-on repository on GitHub.
2. Clone this repo as follows:
`git clone https://github.com/yourGitHubUserName/reportSymbols`
3. From your local folder for the cloned repo, add this repo as your upstream remote:
`git remote add upstream https://github.com/nvdaes/reportSymbols`
4. Link the master branch of this repo with your local master branch, to receive updates from this repo:
`git fetch upstream`
`git branch -u upstream/master`

### Before making changes ###

1. Be sure you are in the master branch:
`git checkout master`
2. Update your master branch:
`git pull`
3. Create a topic branch. For instance, if your changes are related to issue 2, you could do:
`git checkout -b i2`

### Making changes ###

You can make changes in the add-on code, following these guidelines:

#### Code Style ####

##### Encoding #####

- Where Python files contain non-ASCII characters, they should be encoded in UTF-8.
- There should be no Unicode BOM at the start of the file, as this unfortunately breaks one of the translation tools we use (xgettext). Instead, include this as the first line of the file (only if the file contains non-ASCII characters):
# -*- coding: UTF-8 -*-

- Most files should contain CRLF line endings, as this is a Windows project and can't be used on Unix-like operating systems.

##### Indentation #####

- Indentation must be done with tabs (one per level), not spaces.
- When splitting a single statement over multiple lines, just indent one or more additional levels. Don't use vertical alignment; e.g. lining up with the bracket on the previous line.

##### Identifier Names #####

- Functions, variables, properties, etc. should use mixed case to separate words, starting with a lower case letter; e.g.  speakText .
- Classes should use mixed case to separate words, starting with an upper case letter; e.g.  BrailleHandler .
- Constants should be all upper case, separating words with underscores; e.g.  LANGS_WITH_CONJUNCT_CHARS .

##### Translatable Strings #####
- All strings that could be presented to the user should be marked as translatable using the  _()  function; e.g.  _("Text review") .
- All translatable strings should have a preceding translators comment describing the purpose of the string for translators. For example:

# Translators: The name of a category of NVDA commands.
SCRCAT_TEXTREVIEW = _("Text review")
