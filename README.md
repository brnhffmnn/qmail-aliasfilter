# 'qmail-aliasfilter' is a smart filter script for all qmail lovers.

It filters aliases by the domain part of the senders email address,
e.g. mail to `nospam-.example.com@hostname.localhost` will only be delivered to maildir
if the mail comes from the `*.example.com` domain, otherwise the mail will be bounced or dropped.

Here is the example content of the `.qmail-nospam-default` script inside your home directory (`/home/jana`):

    |./qmail-aliasfilter.py
    jana


From now on, you can easily register new accounts or newsletter subscriptions with your `nospam-...` email address
e.g. `nospam-newsletter.example.com@hostname.localhost` for mailings from `newsletter.example.com`

Let's see how the wildcard works. Here are some examples:
- `nospam-example.com@...` -> `example.com` (the strictest, but also the best way to suppress spam)
- `nospam-.example.com@...` -> `*.example.com` (and of course: example.com!)
- `nospam-example.@...` -> `example.*`
- `nospam-.example.@...` -> `*.example.*` (the loosest way, use only for debugging!)
- `nospam-example.com+newsletter.example.org@...` -> a combination of the above methods

There is also the possibility to use qmail-aliasfilter in combination with maildrop

    |./qmail-aliasfilter.py
    |maildrop
    jana

## See also

- https://uberspace.de/dokuwiki/cool:qmail-aliasfilter

## Credits

This script is originally by wibuni (github@wibuni.de) who seems to has vanished from the Internet.