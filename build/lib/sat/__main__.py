#!/usr/bin/env python
import sat
if __name__ == "__main__":
    try:
        sat.start()
    except EOFError:
        exit(0)
    except KeyboardInterrupt:
        exit(0)
