# SmartMetering Dashboard

This SmartMetering Dashboard reads p1 telegrams from SmartMeters (conform DSMR) and stores telegrams in redis streams

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c68f9ceebfc244f080d3243cda81fefb)](https://www.codacy.com/manual/richardvandijk/SmartMeteringDashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=richardvandijk/SmartMeteringDashboard&amp;utm_campaign=Badge_Grade)
[![Known Vulnerabilities](https://snyk.io/test/github/richardvandijk/SmartMeteringDashboard/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/richardvandijk/SmartMeteringDashboard?targetFile=requirements.txt)


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Dutch smart meter with accessible P1 port
[USB p1 kabel](https://www.sossolutions.nl/slimme-meter-kabel)

```
pip install -r requirements.txt
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system



## Contributing

Please read [CONTRIBUTING.md]() for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Richard van Dijk** - *Initial work* - [richardvandijk](https://github.com/richardvandijk)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Basis for code is inspired by [jvhaarst](https://github.com/jvhaarst/DSMR-P1-telegram-reader)
* READMe.md inspired by [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
