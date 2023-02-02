# Introduction

Tiur came from a need to collect static documentation sets from multiple teams, and organize them in a simple, fast, and easy-to-deploy portal.

# Goals

The basic design goals of Tiur are as follows:

1. Make it FAST
2. Make it EASY
3. Make it FLEXIBLE

## Make it FAST

The number one complaint about websites is that they load too slowly. This can be particularly true for corporate enterprise software.

Tiur ensures that the site will load at maximum speed, by using static HTML files rather than using a database.

## Make it EASY

Deploying new websites is difficult. Tiur's approach is to package the entire site as a single container, which can be loaded by Docker, or Kubernetes,
or any other deployment system. 

Instructions are included for building the site from scratch on various Linux systems and cloud providers.

## Make it FLEXIBLE

Existing static documentation systems don't let you organize multiple documentation repositories in one portal. They don't let you group projects into 
hierarchical folders. They also don't have any way to force users to log in, which is a requirement for many corporate sites.

In addition, these other systems also expect that documentation repositories are freely accessible on the Internet or from local files. They can't 
authenticate and download documentation from build systems, such as Jenkins.

Tiur is designed to offer username/password login, LDAP-based login for enterprises, and offers multiple methods of importing documentation.
