try:
    import hindsight
    print("hindsight:", dir(hindsight))
except Exception as e:
    print("No hindsight", e)
try:
    import hindsight_client
    print("hindsight_client:", dir(hindsight_client))
    from hindsight_client import Hindsight
    print("Found Hindsight in hindsight_client!")
except Exception as e:
    print("No hindsight_client", e)
try:
    import hindsight_api
    print("hindsight_api:", dir(hindsight_api))
except Exception as e:
    print("No hindsight_api", e)
