import time
from typing import List, Optional

import torch
import transformers


# class _SentinelTokenStoppingCriteria(transformers.StoppingCriteria):
    
#     def __init__(
#         self, 
#         sentinel_tokens: List[str],
#         tokenizer,
#         sentinel_token_ids,
#         starting_idx,
#         stop_string,
#         num_repeats: int = 3,

#     ):
#         super().__init__()
        
#         self.sentinel_tokens = sentinel_tokens
#         self.tokenizer = tokenizer
#         self.num_repeats = num_repeats
        
#     def __call__(self, input_ids, scores):
        
#         # Check if any sentinel token repeats threshold times
#         for sentinel in self.sentinel_tokens:
#             sentinel_ids = self.tokenizer(sentinel).input_ids
#             if self._check_sentinel(input_ids, sentinel_ids, self.num_repeats):
#                 return True
        
#         return False
    
#     def _check_sentinel(self, input_ids, sentinel_ids, num_repeats):
#         num_found = 0
#         for idx in range(len(input_ids) - len(sentinel_ids) + 1):
#             if torch.equal(input_ids[idx:idx+len(sentinel_ids)], sentinel_ids):
#                 num_found += 1
#                 if num_found >= num_repeats:
#                     return True
#         return False
            
class _SentinelTokenStoppingCriteria(transformers.StoppingCriteria):

    def __init__(self, sentinel_token_ids: torch.LongTensor,
                 starting_idx: int, tokenizer, stop_string: str):
        transformers.StoppingCriteria.__init__(self)
        self.sentinel_token_ids = sentinel_token_ids
        self.starting_idx = starting_idx
        self.stopstring = stop_string
        self.tokenizer = tokenizer
        self.count = 0

    def __call__(self, input_ids: torch.LongTensor,
                 _scores: torch.FloatTensor) -> bool:
        for sample in input_ids:
            trimmed_sample = sample[self.starting_idx:]
            # Can't unfold, output is still too tiny. Skip.
            if trimmed_sample.shape[-1] < self.sentinel_token_ids.shape[-1]:
                continue

            for window in trimmed_sample.unfold(dimension=0, size=self.sentinel_token_ids.shape[-1], step=1):
                chunk  = self.tokenizer.decode(window)
                # print(chunk)
                if self.stopstring in chunk:
                    # if self.count >=1:
                        # print("++++++++++++++")
                        # print(chunk)
                        # print(self.stopstring)
                        # print('stop reason token hit')
                        # print('=======================')
                        # self.count = 0
                    return True
                    # print(self.count)
                    # self.count += 1
                    # return False
                if torch.all(torch.eq(self.sentinel_token_ids, window)):
                    return True
                
        return False


class _MaxTimeCriteria(transformers.StoppingCriteria):

    def __init__(self, max_time: float):
        self.start_time = time.time()
        self.max_time = max_time
        
    def __call__(self, input_ids, scores):
        elapsed = time.time() - self.start_time
        if elapsed > self.max_time:
            print("Stopping due to timeout")
            return True
        return False
        
