try:
    import pkg_resources
    version = pkg_resources.get_distribution(__package__).version
except pkg_resources.DistributionNotFound:
    version = '0.0.0'

