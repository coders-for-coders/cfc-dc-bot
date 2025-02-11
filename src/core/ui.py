class BaseComponent:
    """Base class for Discord UI components"""
    def __init__(self, type: int):
        self.type = type

    def to_dict(self) -> dict:
        """Convert component to Discord API format"""
        raise NotImplementedError("Components must implement to_dict()")

class Button(BaseComponent):
    def __init__(self, label: str, style: int = 1, custom_id: str = None, url: str = None, emoji: str = None, disabled: bool = False):
        """Initialize a button component
        
        Args:
            label: Text shown on the button
            style: Button style (1-5)
                1: Primary (blurple)
                2: Secondary (grey) 
                3: Success (green)
                4: Danger (red)
                5: Link (requires url)
            custom_id: Unique identifier for the button
            url: URL for link buttons
            emoji: Unicode emoji or custom emoji ID
            disabled: Whether the button is disabled
        """
        super().__init__(type=2)  # Button component type
        self.label = label
        self.style = style
        self.custom_id = custom_id
        self.url = url
        self.emoji = emoji
        self.disabled = disabled

        if style == 5 and not url:
            raise ValueError("Link buttons require a URL")
        if style != 5 and not custom_id:
            raise ValueError("Non-link buttons require a custom_id")

    def to_dict(self) -> dict:
        """Convert button to Discord API format"""
        button = {
            "type": self.type,
            "label": self.label,
            "style": self.style,
            "disabled": self.disabled
        }
        
        if self.custom_id:
            button["custom_id"] = self.custom_id
        if self.url:
            button["url"] = self.url
        if self.emoji:
            button["emoji"] = self.emoji

        return button

class ActionRow(BaseComponent):
    def __init__(self, *components):
        """Initialize an action row to hold components
        
        Args:
            *components: Button components to include
        """
        super().__init__(type=1)  # Action row component type
        
        if len(components) > 5:
            raise ValueError("Action rows can only contain up to 5 components")
            
        self.components = list(components)

    def add_component(self, component):
        """Add a component to the action row"""
        if len(self.components) >= 5:
            raise ValueError("Action row already has maximum components")
        self.components.append(component)

    def to_dict(self) -> dict:
        """Convert action row to Discord API format"""
        return {
            "type": self.type,
            "components": [c.to_dict() for c in self.components]
        }
