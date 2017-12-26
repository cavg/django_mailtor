![Travis Build Test](https://travis-ci.org/cavg/django_mailtor.svg?branch=master)

Django Mailtor
-----

Django App mailer to handle emails with templates oriented to reutilization and token replacement.

![Screenshot](https://image.ibb.co/icaEum/Screen_Shot_2017_12_19_at_3_18_36_PM.png)

Features
* Build templates and token by types (img, a, text, date, datetime, time)
* Populate by vars and python object
* Deliver on scheduled
* Log mails and sent timestamp
* Support file attachment

As WYSIWYG editor mailtor use [Quill](https://quilljs.com/) but you can use whatever you want.

## Installing dependencies

Just `pipenv install`

## How to install package

`cd package/django_mailtor/ && python3 setup.py sdist`

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

##### 0.0.8
* Log error tipification in mail instance: fields error_code and error_detail
* Increase test coverage to email html sender
* Minor fixes

##### 0.0.9
* Improve public method comments

##### 0.0.10
* Fix view call get_escape method was renamed

##### 0.0.11
* Include hide pixel to track open email

## License

This theme is released under the [GPLv2 license](https://github.com/cavg/django_mailtor/blob/master/LICENSE.md) (inherited from the original MH Magazine lite WordPress theme).