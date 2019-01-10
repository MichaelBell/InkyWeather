# InkyWeather

This weather status for the Inky pHat is based on the Pimoroni weather
example, but updated to use the Met Office DataPoint weather API instead
of the Yahoo API that is no longer available.

To use it, first register for a Met Office DataPoint service from 
https://register.metoffice.gov.uk/WaveRegistrationClient/public/register.do?service=datapoint

Then create a file called `api_key.txt` containing your API key.

Finally, use `find_id.py` to find the ID of your nearest forecast location
and edit `weather-phat.py` to set the `DATAPOINT_ID` to this value.

Enjoy!
