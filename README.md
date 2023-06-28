# Tiur

![tiur-statue](images/tiur-image.jpeg)

# About Tiur

Tiur is a static documentation site generator written in Python.

*In ancient Armenia, Tiur was revered as the god of wisdom, rhetoric, knowledge, and the arts. He was revered as the scribe and messenger of the supreme god Aramazd.*

# Features of Tiur 

* Aggregates static HTML files 
* Fast and easy to deploy
* Handles multiple repositories and collects them in one site
* Supports authentication for both the site and the repositories
* Includes automatic, built-in search

# Tiur logo

![tiur-statue](images/tiur-logo-filled-350.png)

# More information

More information about the philosophy of Tiur can be found [here](https://github.com/JeremyReimer/Tiur/blob/main/docs/why-tiur.md).

# Status

Tiur is currently in development. Here's what's been written so far:

* Basic HTML and CSS templates for the doc portal (mobile-responsive)
* Database model in Django that allows admin users to create lists of different projects in categories
* Admin code that will scrape projects from a custom URL, with authentication
* Code that will build a left-hand navigation tree with Javascript-enabled dynamic folders
* Basic authentication for the site, with optional LDAP authentication
* Global, full-text indexed search using Lunr.js (searches as you type)
* Customization (so far: upload custom main logo and add custom footer message)
* Dockerization (app deliverable and published as a container on DockerHub)

Here's what's being worked on RIGHT NOW:

* Testing and bug fixes

Here's what's still to come:

* Code cleanup and unit tests
* Automatic versioning support
* More testing and bugfixing
* Full set of documentation

