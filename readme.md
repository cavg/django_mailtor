![Travis Build Test](https://travis-ci.org/cavg/django_mailtor.svg?branch=master)

Django Mailtor
-----

Django App mailer to handle emails with templates oriented to reutilization and token replacement.

Features
* Build templates and token by types (img, a, text, date, datetime, time)
* Populate by vars and python object
* Deliver on scheduled
* Log mails and sent timestamp
* Support file attachment



## Usage

Generate build and install lib

`./install.sh`

This will build the package inside of package/django_mailtor/dist directory



## Configuration
```toml
MAILTOR_ESCAPE_TOKEN = "###"
MAILTOR_DATE_FORMAT = "%A %d de %B del %Y"
MAILTOR_DATETIME_FORMAT = "%A %d de %B del %Y a las %H:%M"
MAILTOR_TIME_FORMAT = "%H:%M:%S"
```


## TODO
- [] Implement task for scheduled delivery

## Contributing

Have you found a bug or got an idea for a new feature? Feel free to use the [issue tracker](https://github.com/cavg/django_mailtor/issues) to let me know. Or make directly a [pull request](https://github.com/cavg/django_mailtor/pulls).

## License

This theme is released under the [GPLv2 license](https://github.com/cavg/django_mailtor/blob/master/LICENSE.md) (inherited from the original MH Magazine lite WordPress theme).