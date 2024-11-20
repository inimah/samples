from .variables import (
    system_start,
    system_end,
    user_start,
    user_end,
    assistant_start,
    assistant_end,
    jinja_environment,
)

import jinja2
env = jinja2.Environment()
env.globals.update(zip=zip)

def _remove_starting_and_ending_whitespace(text):
    # remove whitespace at the beginning and end of each line
    return "\n".join([line.strip() for line in text.split("\n")])


def render_prompt(template_file, prompt_parameter_values):
    template = jinja_environment.get_template(template_file)

    prompt_parameter_values["instruction_start"] = system_start
    prompt_parameter_values["instruction_end"] = system_end
    prompt_parameter_values["input_start"] = user_start
    prompt_parameter_values["input_end"] = user_end
    prompt_parameter_values["output_start"] = assistant_start
    prompt_parameter_values["output_end"] = assistant_end

    # always make these useful constants available in a template
    # make a new function call each time since the date might change during a long-term server deployment
    # today = datetime.now(pytz.timezone("Asia/Shanghai")).date()
    # prompt_parameter_values["today"] = today.strftime("%B %d, %Y")  # May 30, 2023
    # prompt_parameter_values["current_year"] = today.year
    prompt_parameter_values["location"] = "the I.D."

    filled_prompt = template.render(**prompt_parameter_values)
    filled_prompt = _remove_starting_and_ending_whitespace(filled_prompt)


    return filled_prompt

def convert_filled_prompt_to_chat_messages(fp):


    messages = []

    system_s = fp.find(system_start)
    system_e = fp.find(system_end, system_s)
    if system_s < 0:
        # did not find a system message in the prompt, so will put everything inside system for backward compatibility
        messages.append(
            {
                "role": "system",
                "content": fp.strip(),
            }
        )
        return messages

    messages.append(
        {
            "role": "system",
            "content": fp[system_s + len(system_start) : system_e].strip(),
        }
    )

    last_index = 0
    while True:
        user_s = fp.find(user_start, last_index)
        assistant_s = fp.find(assistant_start, last_index)

        if (
            user_s >= 0
            and assistant_s < 0
            or (user_s >= 0 and user_s < assistant_s)
        ):
            user_e = fp.find(user_end, user_s)
            assert user_e >= 0, "Missing closing tag for user"
            last_index = user_e

            messages.append(
                {
                    "role": "user",
                    "content": fp[user_s + len(user_start) : user_e].strip(),
                }
            )
        elif (
            user_s < 0
            and assistant_s >= 0
            or (assistant_s >= 0 and user_s > assistant_s)
        ):
            assistant_e = fp.find(assistant_end, assistant_s)
            assert assistant_e >= 0, "Missing closing tag for assistant"
            last_index = assistant_e
            messages.append(
                {
                    "role": "assistant",
                    "content": fp[
                        assistant_s + len(assistant_start) : assistant_e
                    ].strip(),
                }
            )
        else:
            assert user_s < 0 and assistant_s < 0
            break

    return messages


def convert_filled_prompt_to_chat_messages_non_system(fp, sys_template):


    messages = []

    system_s = fp.find(system_start)
    system_e = fp.find(system_end, system_s)
    
    last_index = 0
    while True:
        user_s = fp.find(user_start, last_index)
        assistant_s = fp.find(assistant_start, last_index)

        if (
            user_s >= 0
            and assistant_s < 0
            or (user_s >= 0 and user_s < assistant_s)
        ):
            user_e = fp.find(user_end, user_s)
            assert user_e >= 0, "Missing closing tag for user"
            last_index = user_e

            messages.append(
                {
                    "role": "user",
                    "content": sys_template + fp[user_s + len(user_start) : user_e].strip(),
                }
            )
        elif (
            user_s < 0
            and assistant_s >= 0
            or (assistant_s >= 0 and user_s > assistant_s)
        ):
            assistant_e = fp.find(assistant_end, assistant_s)
            assert assistant_e >= 0, "Missing closing tag for assistant"
            last_index = assistant_e
            messages.append(
                {
                    "role": "assistant",
                    "content": fp[
                        assistant_s + len(assistant_start) : assistant_e
                    ].strip(),
                }
            )
        else:
            assert user_s < 0 and assistant_s < 0
            break

    return messages