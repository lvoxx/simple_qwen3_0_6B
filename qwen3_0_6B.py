import torch
import threading
import chainlit as cl
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer


class QwenChatbot:
    def __init__(self, model_name="Qwen/Qwen3-0.6B", multi_gpus: bool = False):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"[Init] Loading model: {model_name}")
        print(f"[Init] Device: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)

        # Multi-GPU support
        if multi_gpus and torch.cuda.device_count() > 1:
            print(f"[Init] Multi-GPU enabled: {torch.cuda.device_count()} GPUs")
            model = torch.nn.DataParallel(model)

        self.model = model.to(self.device)
        self.history = []

    async def generate_response(
        self, prompt: str, msg: cl.Message, thinking_mode: bool = False
    ):
        messages = self.history + [{"role": "user", "content": prompt}]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=thinking_mode,
        )

        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )

        # Start generation in background thread
        thread = threading.Thread(
            target=self.model.generate,
            kwargs={
                "inputs": inputs["input_ids"],
                "attention_mask": inputs["attention_mask"],
                "max_new_tokens": 1024,
                "do_sample": True,
                "top_k": 50,
                "top_p": 0.95,
                "temperature": 0.7,
                "streamer": streamer,
            },
        )
        thread.start()

        full_response = ""
        async for token in self._stream_tokens(streamer):
            await msg.stream_token(token)
            full_response += token

        thread.join()

        # Update history
        self.history.append({"role": "user", "content": prompt})
        self.history.append({"role": "assistant", "content": full_response})

        return full_response

    async def _stream_tokens(self, streamer):
        for token in streamer:
            yield token
