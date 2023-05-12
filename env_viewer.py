from typing import Optional, Sequence, Tuple

import jax.numpy as jnp
import matplotlib.animation
import matplotlib.pyplot as plt

import jumanji.environments


class Game2048Viewer:
    COLORS = {
        0: "#ccc0b3",
        2: "#eee4da",
        4: "#ede0c8",
        8: "#f59563",
        16: "#f59563",
        32: "#f67c5f",
        64: "#f65e3b",
        128: "#edcf72",
        256: "#edcc61",
        512: "#edc651",
        1024: "#eec744",
        2048: "#ecc22e",
        4096: "#b784ab",
        8192: "#b784ab",
        16384: "#aa60a6",
        "other": "#f8251d",
        "light_text": "#f9f6f2",
        "dark_text": "#766d64",
        "edge": "#bbada0",
        "bg": "#faf8ef",
    }

    def __init__(
        self,
        name: str = "2048",
        board_size: int = 4,
    ) -> None:
        """Viewer for the 2048 environment.

        Args:
            name: the window name to be used when initialising the window.
            board_size: size of the board.
        """
        self._name = name
        self._board_size = board_size

        # The animation must be stored in a variable that lives as long as the
        # animation should run. Otherwise, the animation will get garbage-collected.
        self._animation: Optional[matplotlib.animation.Animation] = None

    def render(self, state, save: bool = True, path: str = "./2048.png") -> None:
        """Renders the current state of the game board.

        Args:
            state: is the current game state to be rendered.
            save: whether to save the rendered image to a file.
            path: the path to save the rendered image file.
        """
        # Get the figure and axes for the game board.
        fig, ax = self.get_fig_ax()
        # Set the figure title to display the current score.
        fig.suptitle(f"2048    Score: {int(state.score)}", size=20)
        # Draw the game board
        self.draw_board(ax, state)
        # Save the figure as an image file.
        if save:
            fig.savefig(path, bbox_inches="tight", pad_inches=0.5)

        self._display_human(fig)

    def animate(
        self,
        states,
        interval: int = 200,
        blit: bool = False,
        save: bool = True,
        path: str = "./2048.gif",
    ) -> matplotlib.animation.FuncAnimation:
        """Creates an animated gif of the 2048 game board based on the sequence of game states.

        Args:
            states: is a list of `State` objects representing the sequence of game states.
            interval: the delay between frames in milliseconds.
            blit: whether to use blitting to optimize the animation.
            save: whether to save the animation to a file.
            path: the path to save the animation file.

        Returns:
            animation.FuncAnimation: the animation object that was created.
        """
        # Set up the figure and axes for the game board.
        fig, ax = self.get_fig_ax()
        fig.suptitle("2048    Score: 0", size=20)
        plt.tight_layout()

        # Define a function to animate a single game state.
        def animate_state(state_index: int) -> None:
            state = states[state_index]
            self.draw_board(ax, state)
            fig.suptitle(f"2048    Score: {int(state.score)}", size=20)

        # Create the animation object using FuncAnimation.
        self._animation = matplotlib.animation.FuncAnimation(
            fig,
            animate_state,
            frames=len(states),
            blit=blit,
            interval=interval,
        )

        # Save the animation as a gif.
        if save:
            self._animation.save(path)
        return self._animation

    def get_fig_ax(self) -> Tuple[plt.Figure, plt.Axes]:
        """This function returns a `Matplotlib` figure and axes object for displaying the 2048 game board.

        Returns:
            A tuple containing the figure and axes objects.
        """
        # Check if a figure with an id "2048" already exists.
        exists = plt.fignum_exists(self._name)
        if exists:
            # If it exists, get the figure and axes objects.
            fig = plt.figure(self._name)
            ax = fig.get_axes()[0]
        else:
            # If it doesn't exist, create a new figure and axes objects.
            fig = plt.figure(
                self._name,
                figsize=(6.0, 6.0),
                facecolor=self.COLORS["bg"],
            )
            plt.tight_layout()
            plt.axis("off")
            if not plt.isinteractive():
                fig.show()
            ax = fig.add_subplot()
        return fig, ax

    def render_tile(self, tile_value: int, ax: plt.Axes, row: int, col: int) -> None:
        """Renders a single tile on the game board.

        Args:
            tile_value: is the value of the tile on the game board.
            ax: the axes on which to draw the tile.
            row: the row index of the tile on the board.
            col: the col index of the tile on the board.
        """
        # Set the background color of the tile based on its value.
        if tile_value <= 16384:
            rect = plt.Rectangle(
                [col - 0.5, row - 0.5], 1, 1, color=self.COLORS[int(tile_value)]
            )
        else:
            rect = plt.Rectangle(
                [col - 0.5, row - 0.5], 1, 1, color=self.COLORS["other"]
            )
        ax.add_patch(rect)

        if tile_value in [2, 4]:
            color = self.COLORS["dark_text"]
            size = 30
        elif tile_value < 1024:
            color = self.COLORS["light_text"]
            size = 30
        elif tile_value >= 1024 and tile_value < 16384:
            color = self.COLORS["light_text"]
            size = 25
        else:  # tile_value >= 16384:
            color = self.COLORS["light_text"]
            size = 20
        # Empty tiles (each corresponding to the number 1) are not rendered.
        if tile_value != 0:
            ax.text(
                col,
                row,
                str(tile_value),
                color=color,
                ha="center",
                va="center",
                size=size,
                weight="bold",
            )

    def draw_board(self, ax: plt.Axes, state) -> None:
        """Draw the game board with the current state.

        Args:
            ax: the axis to draw the board on.
            state: the current state of the game.
        """
        ax.clear()
        ax.set_xticks(jnp.arange(-0.5, 4 - 1, 1))
        ax.set_yticks(jnp.arange(-0.5, 4 - 1, 1))
        ax.tick_params(
            top=False,
            bottom=False,
            left=False,
            right=False,
            labelleft=False,
            labelbottom=False,
            labeltop=False,
            labelright=False,
        )
        board=state.board
        # Iterate through each cell and render tiles.
        for row in range(0, self._board_size):
            for col in range(0, self._board_size):
                self.render_tile(tile_value=board[row, col], ax=ax, row=row, col=col)

        # Show the image of the board.
        ax.imshow(board)

        # Draw the grid lines.
        ax.grid(color=self.COLORS["edge"], linestyle="-", linewidth=7)

    def close(self) -> None:
        plt.close(self._name)

    def _display_human(self, fig: plt.Figure) -> None:
        if plt.isinteractive():
            # Required to update render when using Jupyter Notebook.
            fig.canvas.draw()
            if jumanji.environments.is_colab():
                plt.show(self._name)
        else:
            # Required to update render when not using Jupyter Notebook.
            fig.canvas.draw_idle()
            # Block for 2 seconds.
            fig.canvas.start_event_loop(2.0)

    def _clear_display(self) -> None:
        if jumanji.environments.is_colab():
            import IPython.display

            IPython.display.clear_output(True)
