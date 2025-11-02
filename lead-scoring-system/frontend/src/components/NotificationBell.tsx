import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import apiClient from "../services/api";

interface Notification {
  id: string;
  notification_type: string;
  title: string;
  message: string;
  link: string | null;
  is_read: boolean;
  created_at: string;
}

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data: unreadCount } = useQuery({
    queryKey: ["unread-count"],
    queryFn: async () => {
      const response = await apiClient.get("/notifications/unread-count");
      return response.data.count;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const { data: notifications } = useQuery({
    queryKey: ["notifications"],
    queryFn: async () => {
      const response = await apiClient.get("/notifications/");
      return response.data;
    },
    enabled: isOpen,
  });

  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId: string) => {
      await apiClient.put(`/notifications/${notificationId}/read`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["unread-count"] });
    },
  });

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      markAsReadMutation.mutate(notification.id);
    }
    if (notification.link) {
      navigate(notification.link);
    }
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <Button variant="outline" onClick={() => setIsOpen(!isOpen)} className="relative">
        🔔
        {unreadCount > 0 && (
          <Badge className="absolute -top-2 -right-2 bg-red-500 text-white text-xs px-1.5 py-0.5">
            {unreadCount}
          </Badge>
        )}
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border z-50">
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="font-semibold">Notifications</h3>
            {unreadCount > 0 && (
              <button
                className="text-sm text-blue-600 hover:underline"
                onClick={async () => {
                  await apiClient.put("/notifications/read-all");
                  queryClient.invalidateQueries({ queryKey: ["notifications"] });
                  queryClient.invalidateQueries({ queryKey: ["unread-count"] });
                }}
              >
                Mark all read
              </button>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto">
            {notifications?.length === 0 ? (
              <p className="p-4 text-center text-gray-500">No notifications</p>
            ) : (
              notifications?.map((notif: Notification) => (
                <div
                  key={notif.id}
                  className={`p-4 border-b hover:bg-gray-50 cursor-pointer ${
                    !notif.is_read ? "bg-blue-50" : ""
                  }`}
                  onClick={() => handleNotificationClick(notif)}
                >
                  <p className="font-medium text-sm">{notif.title}</p>
                  <p className="text-xs text-gray-600">{notif.message}</p>
                  <p className="text-xs text-gray-400 mt-1">{new Date(notif.created_at).toLocaleString()}</p>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

