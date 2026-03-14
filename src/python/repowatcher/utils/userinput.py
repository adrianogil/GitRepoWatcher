
user_input_data = {

}

from prompt_toolkit import PromptSession

prompt_session = PromptSession()

def get_user_input(user_prompt, options=None, default_value=None, cast_type=None, eval_input=False):
    if default_value:
        user_prompt += f" ({default_value})"
    if not user_prompt.strip().endswith(":"):
        user_prompt = user_prompt + ": "
    user_input = prompt_session.prompt(user_prompt)
    if not user_input:
        if options:
            from fzf_wrapper import prompt
            user_choice = prompt(options)
            if user_choice:
                user_input = user_choice[0]
                print(f"> {user_input}")
            else:
                user_input = default_value
        elif default_value:
            user_input = default_value
    if user_input and cast_type:
        if type(user_input) is str and eval_input and (cast_type == int or cast_type == float):
            from asteval import Interpreter
            ae = Interpreter()
            user_input = ae(user_input)
        user_input = cast_type(user_input)
    return user_input
