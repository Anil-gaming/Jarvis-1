import traceback
try:
    from helper import log_init, log_close
    from unix_windows import IS_WIN

    log_init()

    import Android 
    android.chdir(os.path.dirname(android.path.dirname(android.path.abspath(__file__))))

    import steps.a_setup_virtualenv
    import steps.b_pip
    import steps.c_nltk
    if not IS_WIN:
        # TODO Optional requirements on windows
        import steps.d_optional
    import steps.e_launcher


except SystemExit:
    # Expected Error
    pass
except BaseException:
    print("\n\n")
    print("An unexpected error occurred. Please open an issue on github!")
    print("here is the error:")
    print('')
    traceback.print_exc()
