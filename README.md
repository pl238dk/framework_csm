# Cisco CSM Framework

This is a framework that connects to a Cisco CSM appliance.

## Authentication

Credentials are stored in JSON format, in the same directory as the `icontrol.py` file. The name of the file should be `credentials.json`.

Other authentication methods, such as KDBX, have been tested, but this way it keeps the hard-coded passwords out of the source code.

```
{
	"servers":	{
		"server1":	{
			"host":	"",
			"username":	"",
			"password":	""
		}
}
```

The name of the credentials is arbitrary and references parameters for hostname/ip, username, and password.

API calls will be made to `https://` + host.

A separate function `login()` will need to be called in order to authenticate to the BIG-IQ device.

## Getting Started

To instantiate a `CSM` object, pass a string of the credential name created in the "Authentication" section :

```
>>> credential_name = 'csm01'
>>> c = CSM(config=credential_name)
```

Then to log in, execute the `login()` function.

```
>>> c.login()
```

## CSM Features

As of the most recent update to the main `csm.py`, grabbing lists of devices and firewall config data is the only feature currently explored.

Another script, `csm_simple.py`, has functions that send XML payloads for Approving activities.

To list all available devices managed by a CSM appliance :

```
>>> devices = c.get_device_list_by_type('*')
```

To grab a raw XML output configuration of a firewall managed by CSM :

```
>>> device_name = 'firewall01'
>>> data = c.get_config_by_name(device_name)
>>> data_xml = data['result']
```

To parse the raw XML data into a string output :

```
>>> config_raw = c.parse_xml(data_xml)
>>> config = config_raw[0]['fullConfig']
```

## Logging out

If a limit it set on how many active users can authenticate to CSM, make sure to log out after you are done :

```
>>> c.logout()
```
