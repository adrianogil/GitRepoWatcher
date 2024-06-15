import repowatcher.commands.list_categories_command as list_categories_command
import repowatcher.commands.fix_broken_path_command as fix_broken_path_command
import repowatcher.commands.verify_change_command as verify_change_command
import repowatcher.commands.today_commits_command as today_commits_command
import repowatcher.commands.last_commits_command as last_commits_command
import repowatcher.commands.push_commits_command as push_commits_command
import repowatcher.commands.update_batch_command as update_batch_command
import repowatcher.commands.commit_stats_command as commit_stats_command
import repowatcher.commands.delete_repo_command as delete_repo_command
import repowatcher.commands.list_repos_command as list_repos_command
import repowatcher.commands.save_repo_command as save_repo_command
import repowatcher.commands.move_head_command as move_head_command
import repowatcher.commands.get_info_command as get_info_command
import repowatcher.commands.execute_command as execute_command
import repowatcher.commands.import_command as import_command
import repowatcher.commands.export_command as export_command
import repowatcher.commands.help_command as help_command
import repowatcher.commands.edit_command as edit_command


def get_available_commands():
    return [
        list_categories_command,
        fix_broken_path_command,
        last_commits_command,
        commit_stats_command,
        save_repo_command,
        verify_change_command,
        push_commits_command,
        today_commits_command,
        update_batch_command,
        get_info_command,
        execute_command,
        import_command,
        export_command,
        delete_repo_command,
        list_repos_command,
        move_head_command,
        edit_command,
        help_command,
    ]