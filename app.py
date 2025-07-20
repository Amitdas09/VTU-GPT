import streamlit as st
import subprocess
import time
import json
from typing import List, Dict, Generator
import threading
import queue
import os

# Configure the Streamlit page
st.set_page_config(
    page_title="VTU-GPT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_model' not in st.session_state:
    st.session_state.current_model = "llama3.2:3b"
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False
if 'all_chats' not in st.session_state:
    st.session_state.all_chats = {}
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'chat_counter' not in st.session_state:
    st.session_state.chat_counter = 0

def stream_ollama_response(prompt: str, model: str = "llama3.2:3b") -> Generator[str, None, None]:
    """Stream response from Ollama model"""
    try:
        # Create the ollama command
        cmd = ['ollama', 'run', model]
        
        # Start the subprocess
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Send the prompt
        process.stdin.write(prompt + '\n')
        process.stdin.flush()
        process.stdin.close()
        
        # Read the response character by character for streaming effect
        response = ""
        while True:
            char = process.stdout.read(1)
            if not char:
                break
            response += char
            yield response
        
        # Wait for process to complete
        process.wait()
        
        if process.returncode != 0:
            error = process.stderr.read()
            yield f"Error: {error}"
    
    except FileNotFoundError:
        yield "Error: Ollama not found. Please install Ollama and pull the llama3.2:3b model."
    except Exception as e:
        yield f"Error: {str(e)}"

def get_ollama_response(prompt: str, model: str = "llama3.2:3b") -> str:
    """Get complete response from Ollama model"""
    try:
        result = subprocess.run(
            ['ollama', 'run', model],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    
    except subprocess.TimeoutExpired:
        return "Error: Request timed out. Please try again."
    except FileNotFoundError:
        return "Error: Ollama not found. Please install Ollama and pull the llama3.2:3b model."
    except Exception as e:
        return f"Error: {str(e)}"

def check_model_availability(model: str) -> bool:
    """Check if the specified model is available"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        return model in result.stdout
    except:
        return False

def display_chat_message(role: str, content: str, timestamp: str = None):
    """Display a chat message with proper styling"""
    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)
    else:
        with st.chat_message("assistant"):
            st.markdown(content)
    
    if timestamp:
        st.caption(f"*{timestamp}*")

def clear_chat_history():
    """Clear the chat history"""
    st.session_state.chat_history = []
    st.rerun()

def create_new_chat():
    """Create a new chat session"""
    # Save current chat if it has messages
    if st.session_state.chat_history and st.session_state.current_chat_id:
        save_current_chat()
    
    # Create new chat
    st.session_state.chat_counter += 1
    new_chat_id = f"chat_{st.session_state.chat_counter}"
    st.session_state.current_chat_id = new_chat_id
    st.session_state.chat_history = []
    st.rerun()

def save_current_chat():
    """Save current chat to all_chats"""
    if st.session_state.chat_history and st.session_state.current_chat_id:
        # Get chat title from first user message (truncated)
        title = "New Chat"
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                title = msg["content"][:50] + ("..." if len(msg["content"]) > 50 else "")
                break
        
        st.session_state.all_chats[st.session_state.current_chat_id] = {
            "title": title,
            "messages": st.session_state.chat_history.copy(),
            "model": st.session_state.current_model,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def load_chat(chat_id: str):
    """Load a specific chat"""
    if chat_id in st.session_state.all_chats:
        # Save current chat before switching
        if st.session_state.chat_history and st.session_state.current_chat_id:
            save_current_chat()
        
        # Load selected chat
        chat_data = st.session_state.all_chats[chat_id]
        st.session_state.current_chat_id = chat_id
        st.session_state.chat_history = chat_data["messages"].copy()
        st.session_state.current_model = chat_data["model"]
        st.rerun()

def delete_chat(chat_id: str):
    """Delete a specific chat"""
    if chat_id in st.session_state.all_chats:
        del st.session_state.all_chats[chat_id]
        
        # If we deleted the current chat, create a new one
        if st.session_state.current_chat_id == chat_id:
            create_new_chat()
        else:
            st.rerun()

def get_chat_preview(messages: List[Dict], max_length: int = 100) -> str:
    """Get a preview of the chat messages"""
    if not messages:
        return "Empty chat"
    
    # Find first user message
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"]
            return content[:max_length] + ("..." if len(content) > max_length else "")
    
    return "New chat"

def export_chat_history():
    """Export chat history as JSON"""
    if st.session_state.chat_history:
        chat_data = {
            "model": st.session_state.current_model,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "messages": st.session_state.chat_history
        }
        return json.dumps(chat_data, indent=2)
    return None

def main():
    # Header
    st.title("🤖 VTU-GPT")
    st.markdown("Powered by HKBK")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Chat controls
        st.subheader("🔧 Chat Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                clear_chat_history()
        
        with col2:
            if st.button("➕ New Chat", use_container_width=True):
                create_new_chat()
        
        # Chat History Section
        st.subheader("💬 Chat History")
        
        # Auto-save current chat when there are messages
        if st.session_state.chat_history and st.session_state.current_chat_id:
            save_current_chat()
        
        # Display all chats
        if st.session_state.all_chats:
            # Sort chats by last updated (most recent first)
            sorted_chats = sorted(
                st.session_state.all_chats.items(),
                key=lambda x: x[1]["last_updated"],
                reverse=True
            )
            
            for chat_id, chat_data in sorted_chats:
                # Create container for each chat
                chat_container = st.container()
                
                with chat_container:
                    # Show current chat indicator
                    is_current = chat_id == st.session_state.current_chat_id
                    indicator = "🟢" if is_current else "⚪"
                    
                    # Chat title with preview
                    title = chat_data["title"]
                    preview = get_chat_preview(chat_data["messages"])
                    
                    # Create columns for chat item
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        if st.button(
                            f"{indicator} {title}",
                            key=f"load_{chat_id}",
                            help=f"Created: {chat_data['created_at']}\nModel: {chat_data['model']}\nMessages: {len(chat_data['messages'])}",
                            use_container_width=True,
                            disabled=is_current
                        ):
                            load_chat(chat_id)
                    
                    with col2:
                        if st.button(
                            "🗑️",
                            key=f"delete_{chat_id}",
                            help="Delete this chat",
                            use_container_width=True
                        ):
                            delete_chat(chat_id)
                    
                    # Show chat info
                    st.caption(f"📅 {chat_data['last_updated']} | 🤖 {chat_data['model']} | 💬 {len(chat_data['messages'])} messages")
                    st.markdown("---")
        else:
            st.info("No previous chats available")
            
        # Initialize first chat if none exists
        if not st.session_state.current_chat_id:
            create_new_chat()
        
        # Export chat
        if st.session_state.chat_history:
            chat_export = export_chat_history()
            if chat_export:
                st.download_button(
                    label="💾 Export Current Chat",
                    data=chat_export,
                    file_name=f"chat_{st.session_state.current_chat_id}_{int(time.time())}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        # Export all chats
        if st.session_state.all_chats:
            all_chats_export = json.dumps({
                "export_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_chats": len(st.session_state.all_chats),
                "chats": st.session_state.all_chats
            }, indent=2)
            
            st.download_button(
                label="📦 Export All Chats",
                data=all_chats_export,
                file_name=f"all_chats_{int(time.time())}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Statistics
        st.subheader("📈 Statistics")
        
        # Current chat stats
        st.metric("Current Chat Messages", len(st.session_state.chat_history))
        
        # All chats stats
        if st.session_state.all_chats:
            total_chats = len(st.session_state.all_chats)
            total_messages = sum(len(chat["messages"]) for chat in st.session_state.all_chats.values())
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Chats", total_chats)
            with col2:
                st.metric("Total Messages", total_messages)
        
        if st.session_state.chat_history:
            user_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])
            assistant_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "assistant"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("User Messages", user_messages)
            with col2:
                st.metric("Assistant Messages", assistant_messages)
        
        # Instructions
        st.subheader("📚 Instructions")
        st.markdown("""
        1. **Start Chatting**: Type your message below
        2. **General AI Assistant**: This model excels at conversations, Q&A, and general assistance
        3. **Clear Chat**: Use the clear button to start fresh
        """)
    
    # Main chat interface
    st.subheader("💬 Chat Interface")
    
    # Show current chat info
    if st.session_state.current_chat_id:
        chat_info = st.session_state.all_chats.get(st.session_state.current_chat_id)
        if chat_info:
            st.caption(f"📝 **Current Chat:** {chat_info['title']} | 🤖 **Model:** {st.session_state.current_model} | 📅 **Created:** {chat_info['created_at']}")
        else:
            st.caption(f"📝 **New Chat** | 🤖 **Model:** {st.session_state.current_model}")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                display_chat_message(
                    message["role"], 
                    message["content"],
                    message.get("timestamp")
                )
        else:
            st.info("👋 Welcome! Start a conversation by typing a message below.")
    
    # User input
    user_input = st.chat_input("Type your message here...", disabled=st.session_state.is_generating)
    
    if user_input and not st.session_state.is_generating:
        # Create new chat if none exists
        if not st.session_state.current_chat_id:
            create_new_chat()
        
        # Add user message to history
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        
        # Auto-save current chat
        save_current_chat()
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate assistant response
        st.session_state.is_generating = True
        
        with st.chat_message("assistant"):
            # Create placeholder for streaming response
            response_placeholder = st.empty()
            
            # Show loading spinner
            with st.spinner("Thinking..."):
                # Get response from model
                response = get_ollama_response(user_input, st.session_state.current_model)
            
            # Display the response
            response_placeholder.markdown(response)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Auto-save updated chat
            save_current_chat()
        
        st.session_state.is_generating = False
        st.rerun()
    
    # Footer with helpful information
    st.markdown("---")
    with st.expander("🔍 About This Application"):
        st.markdown("""
        **VTU-GPT POWERED BY HKBK**
        
        **Features:**
        - 💬 Real-time chat interface
        - 🔄 Conversation history with chat switching
        - 📱 Multiple chat sessions (like ChatGPT)
        - 🔄 Easy navigation between chats
        - 💾 Export individual or all chats
        - 📊 Comprehensive chat statistics
        - 🎨 Clean, modern UI
        
        **Tips:**
        - Ask questions about any topic for helpful responses
        - Use clear, specific prompts for better results
        - The Llama 3.2 3B model provides balanced performance and speed
        - Use "New Chat" to start fresh conversations
        - Previous chats are automatically saved and accessible
        - Click on any previous chat to continue the conversation
        """)
    
    # System requirements check
    if not check_model_availability(st.session_state.current_model):
        st.error(f"""
        ⚠️ **Model Not Available**
        
        The {st.session_state.current_model} model is not installed. Please run:
        
        ```bash
        ollama pull {st.session_state.current_model}
        ```
        
        Then refresh this page.
        """)

if __name__ == "__main__":
    main()
