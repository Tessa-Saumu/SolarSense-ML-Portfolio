                    PROJECT OVERVIEW

This service is part of the SolarSense AI capstone project.
Model 3 is responsible for evaluating whether installing a solar energy system is financially viable for a customer.

It calculates:

    > Monthly savings from solar energy
    > Annual savings
    > Return on Investment (ROI %)
    > Payback period in years
    > Financial viability classification

The service is exposed as a REST API built with Flask so it can integrate with other models in the system.

WHAT THIS SERVICE DOES:-
Given:
    > Cost of installing the solar system
    > Monthly electricity consumption
    > Monthly solar energy generation
    > Electricity tariff per kWh

The API returns:
    > Monthly savings (USD)
    > Annual savings (USD)
    > ROI percentage
    > Payback period (years)
    > Viability label:-
        >>> Highly Viable
        >>> Moderately Viable
        >>> Not Viable

TECH STACK
    > Python 3
    > Flask
    > flask-cors
    > REST API
    > JSON input/output

PROJECT STRUCTURE
    model_roi_api/
    │
    ├── app.py          # Flask application and ROI logic
    ├── README.md       # Project documentation


