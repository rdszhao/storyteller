'''Feedback Logger - Stores all generation cycles and user feedback in JSON.'''

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import asdict

class FeedbackLogger:
    '''Logs all story generation cycles and user feedback to JSON'''

    def __init__(self, log_dir: str = 'feedback_logs'):
        self.log_dir = log_dir
        self.current_session = None
        self.session_file = None

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def start_session(self, user_request: str, story_type: str):
        '''Start a new story generation session'''
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_id = f'{story_type}_{timestamp}'

        self.current_session = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'user_request': user_request,
            'story_type': story_type,
            'generations': [],
            'user_feedback': None
        }

        self.session_file = os.path.join(self.log_dir, f"{session_id}.json")
        return session_id

    def log_narrative_plan(self, narrative_plan: Any):
        '''Log the narrative plan'''
        if self.current_session:
            self.current_session['narrative_plan'] = asdict(narrative_plan)

    def log_generation(
            self,
            generation_type: str,
            content: str,
            evaluation: Optional[Any] = None,
            revision_count: int = 0,
            chapter_num: Optional[int] = None,
            user_feedback_input: Optional[str] = None
        ):
        '''Log a generation cycle (story, chapter, or revision)'''
        if not self.current_session:
            return

        generation_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': generation_type,  # initial, revision, chapter, user_revision
            'content': content,
            'revision_count': revision_count,
            'chapter_number': chapter_num,
            'user_feedback_input': user_feedback_input
        }

        if evaluation:
            generation_entry['evaluation'] = asdict(evaluation)

        self.current_session['generations'].append(generation_entry)
        self._save_session()

    def log_user_exit_feedback(self, feedback: str, story_content: str):
        '''Log user feedback when exiting'''
        if not self.current_session:
            return

        self.current_session['user_feedback'] = {
            'timestamp': datetime.now().isoformat(),
            'feedback': feedback,
            'final_story': story_content
        }

        self._save_session()

    def _save_session(self):
        '''Save current session to file'''
        if self.current_session and self.session_file:
            with open(self.session_file, 'w') as f:
                json.dump(self.current_session, f, indent=2)

    def get_historical_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        '''Get recent user feedback from previous sessions'''
        feedback_entries = []

        if not os.path.exists(self.log_dir):
            return feedback_entries

        files = [
            os.path.join(self.log_dir, f)
            for f in os.listdir(self.log_dir)
            if f.endswith('.json')
        ]
        # sorted by modification time (newest first)
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        for file_path in files[:limit]:
            try:
                with open(file_path, 'r') as f:
                    session = json.load(f)
                    if session.get('user_feedback'):
                        feedback_entries.append({
                            'session_id': session.get('session_id'),
                            'user_request': session.get('user_request'),
                            'feedback': session['user_feedback']['feedback'],
                            'timestamp': session['user_feedback']['timestamp']
                        })
            except (json.JSONDecodeError, KeyError):
                continue
        return feedback_entries