![Travis Build Test](https://travis-ci.org/cavg/django_mailtor.svg?branch=master)

Django Mailtor
-----

Django App mailer to handle emails with templates oriented to reutilization and token replacement.

![Screenshot](https://image.ibb.co/icaEum/Screen_Shot_2017_12_19_at_3_18_36_PM.png)

Features:
* Build templates and token by types (img, a, text, date, datetime, time)
* Populate by vars and python object
* Deliver on scheduled
* Log mails and sent timestamp
* Support file attachment
* Opened email tracker

As WYSIWYG editor mailtor use [Quill](https://quilljs.com/) but you can use whatever you want.

## Installing dependencies

Just `pipenv install`

## How to build package

`./build.sh`

This will build the package inside of package/django_mailtor/dist directory

## Fixtures: sample capabilities

`python3 manage.py loaddata mail_template_entity`


## Configuration
```toml
MAILTOR_ESCAPE_TOKEN = "###"
MAILTOR_DATE_FORMAT = "%A %d de %B del %Y"
MAILTOR_DATETIME_FORMAT = "%A %d de %B del %Y a las %H:%M"
MAILTOR_TIME_FORMAT = "%H:%M:%S"
```

## TODO
- [] Implement task for scheduled delivery
- [] Implement in subject var replacements


## Test coverage

`./test.sh`

## Contributing

Have you found a bug or got an idea for a new feature? Feel free to use the [issue tracker](https://github.com/cavg/django_mailtor/issues) to let me know. Or make directly a [pull request](https://github.com/cavg/django_mailtor/pulls).

## Changelog

##### 0.0.31
* Fix error sending mails cc params

##### 0.0.29
* Fix error sending mails

##### 0.0.28
* fix bcc, cc

##### 0.0.25
* naive tz mail sent_at

##### 0.0.24
* to param as array

##### 0.0.23
* fix bug sending html emails and plain text

##### 0.0.22
* fix bug sending html emails

##### 0.0.21
* increase size error log

##### 0.0.19
* fix tracking_open

##### 0.0.15
* upgrade dependency toolbox

##### 0.0.14
* switch index from / to home/

##### 0.0.13
* try again fix error populate with method Mail.try_again_populate
* prevent send scheduled emails
* prevent send again emails already sent

##### 0.0.12
* Move MyHTMLParser to django_toolbox dependency

##### 0.0.11
* Include hide pixel to track open email

##### 0.0.10
* Fix view call get_escape method was renamed

##### 0.0.9
* Improve public method comments

##### 0.0.8
* Log error classification in mail instance into fields error_code and error_detail
* Increase test coverage to email html sender
* Minor fixes


## License

This theme is released under the [GPLv2 license](https://github.com/cavg/django_mailtor/blob/master/LICENSE.md) (inherited from the original MH Magazine lite WordPress theme).